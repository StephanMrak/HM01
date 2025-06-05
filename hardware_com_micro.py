import signal
import spidev
import gpiod
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
import queue
import time
import argparse
from threading import Thread
from queue import Empty as QueueEmpty
from concurrent.futures import ThreadPoolExecutor
import os
from datetime import timedelta, datetime
from scipy.signal import find_peaks
import scipy
import itertools
import pandas as pd
import copy
import profile
import pstats
import hmsysteme

# Constants
SPI_DEVICE = "/dev/spidev0.0"
GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE = 17
SPI_SPEED = 15000000  # Pi5: allows 5MHz increments
BITS_PER_WORD = 10
#DATA_SIZE = 4972 * 2  # 4972 samples, 2 bytes each
DATA_SIZE = 4756 * 2  # 4756 samples, 2 bytes each
MODE = 0
FREQUENCY = 416666
REF_VOLTAGE = 3.3
stop_flag = multiprocessing.Value('b', False)  # Shared flag for stopping

#Apparat
widthD, heigthD = 0.410, 0.2005
c = 1595
z__1 = 0.0
z__2 = z__1
z__3 = 0.0
z__4 = z__3
x__2 = widthD
x__3 = widthD
y__3 = heigthD
y__4 = heigthD
s = (z__3 - z__1) / heigthD


def getTimeDifferences(x, y):
    zUpper = -0.0
    zLower = -0.0
    s = (zLower - zUpper) / heigthD
    z = y * s + zUpper
    l1 = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    l2 = np.sqrt((widthD - x) ** 2 + y ** 2 + z ** 2)
    l3 = np.sqrt((widthD - x) ** 2 + (heigthD - y) ** 2 + z ** 2)
    l4 = np.sqrt(x ** 2 + (heigthD - y) ** 2 + z ** 2)

    t12 = (l2 - l1) / c
    t13 = (l3 - l1) / c
    t14 = (l4 - l1) / c
    t23 = (l3 - l2) / c
    t24 = (l4 - l2) / c
    t34 = (l4 - l3) / c

    return [t12, t13, t14, t23, t24, t34]


def getJacobian2d(x, y):
    t40 = y * s + z__1;
    t41 = y - y__4;
    t39 = t40 * t40;
    t50 = x * x + t39;
    t33 = np.power(t41 * t41 + t50, -.5);
    t54 = t33 * x;
    t42 = y - y__3;
    t43 = x__3 - x;
    t31 = np.power(t42 * t42 + t43 * t43 + t39, -.5);
    t38 = t40 * s + y;
    t53 = t31 * (t38 - y__3);
    t44 = x__2 - x;
    t47 = y * y;
    t32 = np.power(t44 * t44 + t39 + t47, -.5);
    t52 = t32 * t44;
    t51 = t33 * (t38 - y__4);
    t35 = np.power(t47 + t50, -.5);
    t34 = t35 * x;
    t30 = t35 * t38;
    t29 = t31 * t43;
    t28 = t32 * t38;
    return np.matrix([[t34 + t52, t30 - t28], [t34 + t29, t30 - t53], [t34 - t54, t30 - t51], [t29 - t52, t28 - t53],
                      [-t52 - t54, t28 - t51], [-t29 - t54, -t51 + t53]])


def getResidual2d(x, y, t):
    t__12, t__13, t__14, t__23, t__24, t__34 = t
    t73 = y * s + z__1;
    t72 = t73 * t73;
    t80 = x * x + t72;
    t78 = y * y;
    t77 = x - x__2;
    t76 = x - x__3;
    t75 = y - y__3;
    t74 = y - y__4;
    t71 = np.sqrt(t78 + t80);
    t70 = np.sqrt(t74 * t74 + t80);
    t69 = np.sqrt(t77 * t77 + t72 + t78);
    t68 = np.sqrt(t75 * t75 + t76 * t76 + t72);
    return np.matrix(
        [[c * t__12 - t69 + t71], [c * t__13 - t68 + t71], [c * t__14 - t70 + t71], [c * t__23 - t68 + t69],
         [c * t__24 + t69 - t70], [c * t__34 + t68 - t70]])


def cleanup(signum, frame):
    global stop_flag
    if not stop_flag.value:
        stop_flag.value = True
        print("\nCaught exit signal")


# Find positive peaks in the area of the onset
def extract_indices(peakIdx, onset, peaksBefore=1, peaksAfter=1, max_distance=100):
    # Find the next index in peakIdx that is greater than or equal to onset
    closest_index = next((idx for idx in peakIdx if idx >= onset), None)
    if closest_index is None:
        return []

    # Find the position of the closest index in the peakIdx list
    pos = peakIdx.tolist().index(closest_index)

    # Extract indices around the given index
    start = max(0, pos - peaksBefore)

    # Adjust the start index if the distance from onset to start exceeds max_distance
    while start < pos and (onset - peakIdx[start]) > max_distance:
        start += 1  # Move the start index forward to reduce the distance

    end = min(len(peakIdx), pos + peaksAfter)

    return peakIdx[start:end]


def compute_aic_optimized(data, offset, epsilon=1e-10):
    # Left-side variance initialization using NumPy
    left_var_calc = OnlineVariance.from_numpy(data[1:offset - 1])

    # Right-side variance initialization using NumPy
    sampleLength = len(data)
    right_var_calc = OnlineVariance.from_numpy(data[offset: sampleLength - offset - 1])

    # Compute AIC for each i using recursive variance
    aic = np.empty(sampleLength - 2 * offset - 1)
    outIdx = 0
    for i in range(offset + 1, sampleLength - offset - 1):
        left_var_calc.update(data[i - 1])  # Expand left-side
        right_var_calc.remove(data[i])  # Shrink right-side

        var_left = left_var_calc.variance() + epsilon
        var_right = right_var_calc.variance() + epsilon

        aic[outIdx] = (i * np.log(var_left) + (sampleLength - i) * np.log(var_right))
        outIdx += 1

    return aic


def getMinAic(data, offset, end, epsilon=1e-10):
    # Left-side variance initialization using NumPy
    left_var_calc = OnlineVariance.from_numpy(data[1:offset - 1])

    # Right-side variance initialization using NumPy
    sampleLength = len(data)
    right_var_calc = OnlineVariance.from_numpy(data[offset: sampleLength - 1])

    # Compute AIC for each i using recursive variance
    minValue = 1e6
    minIndex = offset
    i = offset + 1
    while i < end:
        left_var_calc.update(data[i - 1])  # Expand left-side
        right_var_calc.remove(data[i])  # Shrink right-side

        var_left = left_var_calc.variance() + epsilon
        var_right = right_var_calc.variance() + epsilon

        aicVal = i * np.log(var_left) + (sampleLength - i) * np.log(var_right)
        if (aicVal < minValue):
            minValue = aicVal
            minIndex = i
        i += 1

    return minIndex


class OnlineVariance:
    """ Efficiently compute variance incrementally (Welford's algorithm). """

    def __init__(self, n=0, mean=0.0, m2=0.0):
        self.n = n
        self.mean = mean
        self.m2 = m2  # Sum of squared differences

    def update(self, x):
        """ Add a new data point and update variance """
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.m2 += delta * delta2

    def remove(self, x):
        """ Remove a data point (used for sliding window updates) """
        if self.n <= 1:
            self.n = 0
            self.mean = 0.0
            self.m2 = 0.0
            return
        self.n -= 1
        delta = x - self.mean
        self.mean -= delta / self.n
        self.m2 -= delta * (x - self.mean)

    def variance(self):
        """ Return variance (unbiased estimate for n > 1) """
        return self.m2 / (self.n - 1) if self.n > 1 else 0.0

    @classmethod
    def from_numpy(cls, data):
        """ Create an OnlineVariance object initialized from NumPy data """
        n = len(data)
        if n < 2:
            return cls()
        mean = np.mean(data)
        m2 = np.sum((data - mean) ** 2)  # Compute sum of squared differences
        return cls(n=n, mean=mean, m2=m2)


def process_data(data):
    ch1, ch2, ch3, ch4 = data
    sos = scipy.signal.butter(8, 45000, 'low', fs=FREQUENCY, output='sos')
    # Filter
    factor = REF_VOLTAGE / np.power(2, BITS_PER_WORD)
    dataFiltered = (scipy.signal.sosfilt(sos, ch1 * factor), scipy.signal.sosfilt(sos, ch2 * factor),
                    scipy.signal.sosfilt(sos, ch3 * factor), scipy.signal.sosfilt(sos, ch4 * factor))

    offset = 20
    sampleLength = len(ch1)
    searchWindow = int((1.5 * max(widthD, heigthD)) / (1 / FREQUENCY * c))
    onsetIdx1 = getMinAic(dataFiltered[0], offset, sampleLength - offset - 1)
    offsetForFollowing = onsetIdx1 - searchWindow
    endForFollowing = onsetIdx1 + searchWindow
    if (endForFollowing > sampleLength or offsetForFollowing < 0):
        print("Data not considered due to onset position!")
        return (False, [100, 100], 1e6, 1e6, [0, 0, 0, 0, 0, 0], [0, 0, 0, 0])

    onsetIdx2 = getMinAic(dataFiltered[1], offsetForFollowing, endForFollowing)
    onsetIdx3 = getMinAic(dataFiltered[2], offsetForFollowing, endForFollowing)
    onsetIdx4 = getMinAic(dataFiltered[3], offsetForFollowing, endForFollowing)
    onsetV = [onsetIdx1, onsetIdx2, onsetIdx3, onsetIdx4]

    # Stop here for too big diffs in onsets
    maxOnsettDiff = max(abs(x - y) for x, y in itertools.combinations(onsetV, 2))
    print(f"Max onset difference: {maxOnsettDiff}")
    if (maxOnsettDiff >= searchWindow):
        print("Data not considered due to onset differences!")
        return (False, [100, 100], 1e6, 1e6, [0, 0, 0, 0, 0, 0], [0, 0, 0, 0])

    # Detect peaks in the area of the onset
    peakVectors = []
    peaksBefore = 1
    peaksAfter = 1
    for idx, onset in enumerate(onsetV):
        peakIdx, _ = find_peaks(dataFiltered[idx], distance=1, height=0.2, width=1)
        if len(peakIdx) == 0:
            break
        indices = extract_indices(peakIdx, onset, peaksBefore, peaksAfter)
        if len(indices) == 0:
            break
        peakVectors.append(indices)

    if len(peakVectors) < 4:
        print("Data not considered due to missing peaks!")
        return (False, [100, 100], 1e6, 1e6, [0, 0, 0, 0, 0, 0], [0, 0, 0, 0])

        # Get all possible combinations of peaks and calculate the time difference between them
    combinations = list(itertools.product(*peakVectors))
    lagsForSequence = []
    deltaTime = 1 / FREQUENCY
    for combination in combinations:
        peakIndices = list(combination)
        if peakIndices:
            lagAic12 = (peakIndices[1] - peakIndices[0]) * deltaTime
            lagAic13 = (peakIndices[2] - peakIndices[0]) * deltaTime
            lagAic14 = (peakIndices[3] - peakIndices[0]) * deltaTime
            lagAic23 = (peakIndices[2] - peakIndices[1]) * deltaTime
            lagAic24 = (peakIndices[3] - peakIndices[1]) * deltaTime
            lagAic34 = (peakIndices[3] - peakIndices[2]) * deltaTime
            lagsForSequence.append([lagAic12, lagAic13, lagAic14, lagAic23, lagAic24, lagAic34])

            # Calculate the position estimate
    posEstimate = np.matrix([[widthD / 2], [heigthD / 2]])
    minAbsSumTimeDiff = 1e6
    minNormRes = 1e6
    res = []
    isValid = False
    validLags = []
    validPosition = [100, 100]
    for lag in lagsForSequence:
        posEstimate = np.matrix([[widthD / 2], [heigthD / 2]])
        maxIter = 50
        for i in range(1, maxIter):
            J = getJacobian2d(posEstimate[0, 0], posEstimate[1, 0])
            res = getResidual2d(posEstimate[0, 0], posEstimate[1, 0], lag)
            deltaPosition = np.linalg.inv((J.transpose() * J)) * J.transpose() * res
            positionChangeLength = np.linalg.norm(deltaPosition)
            if (positionChangeLength > 0.02):
                deltaPosition = 0.02 / positionChangeLength * deltaPosition
            posEstimate = posEstimate - deltaPosition

            if (np.linalg.norm(deltaPosition) < 1e-4):
                break

            if (posEstimate[0][0] < 0) or (posEstimate[0][0] > widthD) or (posEstimate[1][0] < 0) or (
                    posEstimate[1][0] > heigthD):
                break

        isInWindow = (posEstimate[0][0] > 0) and (posEstimate[0][0] < widthD) and (posEstimate[1][0] > 0) and (
                    posEstimate[1][0] < heigthD)
        if (isInWindow):
            perfectTimeDiff = getTimeDifferences(posEstimate[0, 0], posEstimate[1, 0])
            absSumTimeDiff = sum(abs(np.array(perfectTimeDiff) - np.array(lag)))
            normResVec = np.linalg.norm(res)
            if (minAbsSumTimeDiff > absSumTimeDiff):
                isValid = True
                minAbsSumTimeDiff = absSumTimeDiff
                minNormRes = normResVec
                validLags = lag
                print(f"Position estimate: {posEstimate}")
                validPosition = posEstimate

    return (isValid, validPosition, minNormRes, minAbsSumTimeDiff, validLags, peakVectors)


def data_processing(data_queue, stop_flag, debug, process):
    if not process:
        print("Processing disabled. Exiting data_processing.")
        return

    batch_data = []  # Stores raw data for the batch
    batch_results = []  # Stores results from process_data for the batch
    batch_duration = 0.1  # 100ms in seconds
    batch_counter = 0
    batch_start_time = None
    processing_tasks = []  # Track processing tasks for the current batch

    def analyze_batch(batch_data, batch_results, batch_id):
        # Placeholder for batch analysis logic
        print(f"Analyzing batch {batch_id}")
        minRes = 1e6
        minPos = [100, 100]
        for result in batch_results:
            isValid, positionEstimate, minNormRes, minAbsSumTimeDiff, validLags, peakVectors = result
            if (isValid and (minRes > minAbsSumTimeDiff)):
                minRes = minAbsSumTimeDiff
                minPos = positionEstimate
                print(f"Candidate position estimate: {positionEstimate}")
                print(f"Candidate normRes: {minNormRes}")
                print(f"Candidate absSumTimeDiff: {minAbsSumTimeDiff}")

        print(f"Resulting position estimate: {minPos}")

        if debug:
            # Ensure the directory exists
            os.makedirs("debug_data", exist_ok=True)
            # Add a timestamp to the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_data/batch_{batch_id}_{timestamp}.npy"
            np.save(filename, np.array(batch_data, dtype=np.int16))
            print(f"Saved batch {batch_id} to disk: {filename}")

    with ThreadPoolExecutor() as executor:
        while not stop_flag.value:
            try:
                # Get data from the queue without waiting if data is already available
                ch1, ch2, ch3, ch4 = copy.deepcopy(data_queue.get_nowait())
                batch_data.append((ch1, ch2, ch3, ch4))

                # Start the batch timer if it's the first data in the batch
                if batch_start_time is None:
                    batch_start_time = time.time()

                # Submit the processing task to the thread pool and store the future
                future = executor.submit(process_data, (ch1, ch2, ch3, ch4))
                processing_tasks.append(future)

            except QueueEmpty:
                # No new data arrived, check if a batch is ongoing and if it's time to finalize it
                if batch_start_time is not None and (time.time() - batch_start_time >= batch_duration):
                    # Wait for all processing tasks in the current batch to complete
                    batch_results = [future.result() for future in processing_tasks]

                    # Analyze the batch after all data has been processed
                    analyze_batch(batch_data, batch_results, batch_counter)
                    batch_data = []  # Reset the batch data
                    batch_results = []  # Reset the batch results
                    processing_tasks = []  # Reset the processing tasks
                    batch_counter += 1
                    batch_start_time = None  # Reset the batch timer

    # Ensure any remaining data in the batch is processed and analyzed before exiting
    if batch_data:
        # Wait for all processing tasks in the current batch to complete
        batch_results = [future.result() for future in processing_tasks]

        # Analyze the final batch
        analyze_batch(batch_data, batch_results, batch_counter)
    print("Data Processing exiting...")


def receiver_process(queue, data_queue, stop_flag, plot, process):
    try:
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.mode = MODE
        spi.bits_per_word = BITS_PER_WORD
        spi.max_speed_hz = SPI_SPEED

        with gpiod.request_lines(
                GPIO_CHIP,
                consumer="spi_interrupt_handler",
                config={GPIO_LINE: gpiod.LineSettings(
                    direction=gpiod.line.Direction.INPUT,
                    edge_detection=gpiod.line.Edge.RISING
                )}
        ) as request:
            print("Waiting for SPI data-ready interrupt...")
            recCounter = 0

            while not stop_flag.value:
                if request.wait_edge_events(timedelta(seconds=1)):
                    events = request.read_edge_events()
                    for event in events:
                        if event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                            rx_buffer = spi.xfer3([0] * DATA_SIZE)
                            print(f"Received {len(rx_buffer)} bytes from SPI {recCounter}")

                            data = np.array(rx_buffer, dtype=np.uint8).astype(np.uint16)
                            receivedData = ((data[1::2] << 8) | data[0::2]).astype(np.int16)

                            ch1 = receivedData[4::4] - receivedData[0]
                            ch2 = receivedData[5::4] - receivedData[1]
                            ch3 = receivedData[6::4] - receivedData[2]
                            ch4 = receivedData[7::4] - receivedData[3]

                            # Only add to the plotting queue if the plot flag is set
                            if plot:
                                queue.put((recCounter, ch1, ch2, ch3, ch4))

                            # Only add to the data processing queue if the process flag is set
                            if process:
                                data_queue.put((ch1, ch2, ch3, ch4))

                            recCounter += 1
    except Exception as e:
        print(f"Error in receiver_process: {e}")
    finally:
        spi.close()
        print("Receiver exiting...")


# **Plotter Function (Runs in Main Thread)**
def plotter_function(queue, stop_flag, plot):
    """ Listens for data and plots it in the main thread. """

    if not plot:
        return

    plt.ion()  # Turn on interactive mode
    figures = []  # Store references to figures to keep them alive

    while not stop_flag.value or not queue.empty():
        try:
            # Get data from the queue (non-blocking)
            try:
                recCounter, ch1, ch2, ch3, ch4 = queue.get(timeout=0.1)  # Short timeout
            except Exception as e:
                # No data in the queue, continue to process events
                plt.pause(0.1)  # Allow the event loop to process
                continue

            # Create a new plot window
            fig, ax = plt.subplots()
            ax.plot(ch1, label="CH1", marker='o')
            ax.plot(ch2, label="CH2", marker='x')
            ax.plot(ch3, label="CH3", marker='s')
            ax.plot(ch4, label="CH4", marker='d')
            ax.legend()
            ax.set_title(f"SPI Data Package {recCounter}")
            ax.set_xlabel("Sample Index")
            ax.set_ylabel("Amplitude")
            ax.grid(True)

            # Draw the plot
            plt.draw()
            plt.pause(0.1)  # Short pause to refresh the plot

            # Store the figure reference to keep it alive
            figures.append(fig)

        except KeyboardInterrupt:
            break

    print("Plotter exiting...")


def load_and_enqueue_data(npy_file, data_queue):
    data = np.load(npy_file)  # Load the npy file
    for item in data:
        data_queue.put(item)  # Enqueue the loaded data
    print("Data from npy file loaded into queue.")

def hardware_com_micro(threadname, path, q, q4, preq, warmupqueue, size):
    while True:
        parser = argparse.ArgumentParser(description="SPI Data Processing")
        parser.add_argument("-p", action="store_true", help="Enable plotting")
        parser.add_argument("-r", action="store_true", help="Enable processing")
        parser.add_argument("-d", action="store_true", help="Enable debug mode (save batch data to disk)")
        parser.add_argument("-f", type=str, help="File name to load data from (optional)")
        args = parser.parse_args()

        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)

        queue = multiprocessing.Queue(maxsize=100)  # Increased queue size
        data_queue = multiprocessing.Queue(maxsize=100)

        # Pass the plot and process flags to the receiver process
        receiver = multiprocessing.Process(target=receiver_process, args=(queue, data_queue, stop_flag, args.p, args.r))

        # If a file name is provided, load data
        if args.f:
            folder_name = "debug_data"  # Change this if needed
            file_path = os.path.join(os.path.dirname(__file__), folder_name, args.f)

            if os.path.exists(file_path):
                load_and_enqueue_data(file_path, data_queue)
            else:
                print(f"Error: File '{file_path}' not found.")
                exit(1)

        processor = multiprocessing.Process(target=data_processing, args=(data_queue, stop_flag, args.d, args.r))

        receiver.start()
        processor.start()

        plotter_function(queue, stop_flag, args.p)

        receiver.join()
        processor.join()

        print("Ciao")

