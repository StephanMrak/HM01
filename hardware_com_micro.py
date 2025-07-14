import signal
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
import time
import argparse
from queue import Empty as QueueEmpty
from concurrent.futures import ThreadPoolExecutor
import os
from datetime import timedelta, datetime
from scipy.signal import find_peaks
import copy
import hmsysteme
import scipy
import itertools
from numba import njit
import sys
import re
from scipy.optimize import fsolve

# Constants
SPI_DEVICE = "/dev/spidev0.0"
GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE_DATA_RDY = 17
GPIO_LINE_NRST = 4
SPI_SPEED = 30000000  # Pi5: allows 5MHz increments
BITS_PER_WORD = 10
DATA_SIZE = 4972 * 2  # x samples, with 2 bytes each
MODE = 0
FREQUENCY = 454000
REF_VOLTAGE = 3.3
stop_flag = multiprocessing.Value('b', False)  # Shared flag for stopping

d_lenght = 0.341
pixelw = d_lenght / hmsysteme.get_size()[0]


widthD, heigthD = 0.370, 0.215
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


# === Parameters ===
a = 0.017  # distance from boundary to receiver (in c2 region)
c1 = c  # speed of sound in sheet
c2 = 330.0  # speed of sound in surroundings
tMax = 1 / 454000  # given time difference
xMax = .5
yMax = .3
resPos = 0.005  # resolution (number of points in each axis)
resX = int(xMax / resPos) + 1
resY = int(yMax / resPos) + 1
# === Ranges ===
x_range = np.linspace(0, xMax, resX)
y_range = np.linspace(yMax, 0, resY)

# === Heatmap values ===
u_map = np.full((resY, resX), np.nan)


# === Equation to solve for each (x, y) ===
def solve_u(x, y):
    def func(u):
        T_RM1 = np.sqrt(x ** 2 + y ** 2) / c1 + a / c2
        T_UM1 = np.sqrt(x ** 2 + (y - u) ** 2) / c1 + np.sqrt(a ** 2 + u ** 2) / c2
        return T_RM1 - T_UM1 - tMax

    # Initial guess for u
    u0 = 0

    try:
        sol = fsolve(func, u0)
        u_val = sol[0]
        if 0 <= u_val <= y:  # Physically valid
            return u_val
    except Exception:
        pass

    return np.nan


# === Compute heatmap ===
for i, x in enumerate(x_range):
    for j, y in enumerate(y_range):
        u_map[j, i] = solve_u(x, y)

# === Plot heatmap ===
u2 = np.fliplr(u_map)  # Flip left-right
u3 = np.flipud(u2)  # Then flip up-down
u4 = np.flipud(u_map)  # Just flip up-down


@njit
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


@njit
def getJacobian2d(x, y, y__1, y__2, y__3, y__4):
    t43 = y * s + z__1;
    t44 = y - y__4;
    t42 = t43 * t43;
    t55 = x * x + t42;
    t36 = np.power(t44 * t44 + t55, -.5);
    t60 = t36 * x;
    t45 = y - y__3;
    t48 = x - x__3;
    t33 = np.power(t45 * t45 + t48 * t48 + t42, -.5);
    t54 = t43 * s + y;
    t59 = t33 * (-y__3 + t54);
    t58 = t33 * t48;
    t46 = y - y__2;
    t49 = x - x__2;
    t34 = np.power(t46 * t46 + t49 * t49 + t42, -.5);
    t57 = t34 * t49;
    t56 = t36 * (-y__4 + t54);
    t47 = y - y__1;
    t37 = np.power(t47 * t47 + t55, -.5);
    t32 = t37 * (-y__1 + t54);
    t35 = t37 * x;
    t31 = t34 * (-y__2 + t54);
    return np.array([[t35 - t57, t32 - t31], [t35 - t58, t32 - t59], [t35 - t60, t32 - t56], [t57 - t58, t31 - t59], [t57 - t60, t31 - t56], [t58 - t60, -t56 + t59]])


@njit
def getResidual2d(x, y, t, y__1, y__2, y__3, y__4):
    t__12, t__13, t__14, t__23, t__24, t__34 = t
    t80 = y * s + z__1;
    t79 = t80 * t80;
    t88 = x * x + t79;
    t86 = x - x__2;
    t85 = x - x__3;
    t84 = y - y__1;
    t83 = y - y__2;
    t82 = y - y__3;
    t81 = y - y__4;
    t78 = np.sqrt(t84 * t84 + t88);
    t77 = np.sqrt(t81 * t81 + t88);
    t76 = np.sqrt(t83 * t83 + t86 * t86 + t79);
    t75 = np.sqrt(t82 * t82 + t85 * t85 + t79);
    return np.array([[c * t__12 - t76 + t78], [c * t__13 - t75 + t78], [c * t__14 - t77 + t78], [c * t__23 - t75 + t76], [c * t__24 + t76 - t77], [c * t__34 + t75 - t77]])


# Find positive peaks in the area of the onset
@njit
def extract_indices(peakIdx, onset, peaksBefore=1, peaksAfter=1, max_distance=50):
    # Find the next index in peakIdx that is greater than or equal to onset
    closest_index = None
    for idx in peakIdx:
        if idx >= onset:
            closest_index = idx
            break  # Stop at the first match
    # closest_index = next((idx for idx in peakIdx if idx >= onset), None)
    if closest_index is None:
        return np.empty(0, dtype=np.int64)

    # Find the position of the closest index in the peakIdx list
    pos = -1
    for i in range(len(peakIdx)):
        if peakIdx[i] == closest_index:
            pos = i
            break  # Stop once found
    # pos = peakIdx.tolist().index(closest_index)

    # Extract indices around the given index
    start = max(0, pos - peaksBefore)

    # Adjust the start index if the distance from onset to start exceeds max_distance
    while start < pos and (onset - peakIdx[start]) > max_distance:
        start += 1  # Move the start index forward to reduce the distance

    end = min(len(peakIdx), pos + peaksAfter)

    return peakIdx[start:end]


@njit
def update_variance(state, x):
    """ Update the variance state with a new data point. """
    n, mean, m2 = state
    n += 1
    delta = x - mean
    mean += delta / n
    delta2 = x - mean
    m2 += delta * delta2
    return (n, mean, m2)


@njit
def remove_variance(state, x):
    """ Remove a data point from the variance state. """
    n, mean, m2 = state
    if n <= 1:
        return (0, 0.0, 0.0)
    n -= 1
    delta = x - mean
    mean -= delta / n
    m2 -= delta * (x - mean)
    return (n, mean, m2)


@njit
def compute_variance(state):
    """ Compute variance from state. """
    n, mean, m2 = state
    return m2 / (n - 1) if n > 1 else 0.0


@njit
def var_state_from_numpy(data):
    """ Initialize an OnlineVariance state from NumPy array. """
    n = len(data)
    mean = np.mean(data)
    m2 = np.sum((data - mean) ** 2)
    return (n, mean, m2)


@njit
def compute_aic_optimized(data, offset, epsilon=1e-10):
    # Left-side variance initialization using NumPy
    left_var_state = var_state_from_numpy(data[1:offset - 1])

    # Right-side variance initialization using NumPy
    sampleLength = len(data)
    right_var_state = var_state_from_numpy(data[offset: sampleLength - offset - 1])

    # Compute AIC for each i using recursive variance
    aic = np.empty(sampleLength - 2 * offset - 1)
    outIdx = 0
    for i in range(offset + 1, sampleLength - offset - 1):
        left_var_state = update_variance(left_var_state, data[i - 1])  # Expand left-side
        right_var_state = remove_variance(right_var_state, data[i])  # Shrink right-side

        var_left = compute_variance(left_var_state) + epsilon
        var_right = compute_variance(right_var_state) + epsilon

        aic[outIdx] = (i * np.log(var_left) + (sampleLength - i) * np.log(var_right))
        outIdx += 1

    return aic


@njit
def getMinAic(data, offset, end, epsilon=1e-10):
    # Left-side variance initialization using NumPy
    left_var_state = var_state_from_numpy(data[1:offset - 1])

    # Right-side variance initialization using NumPy
    sampleLength = len(data)
    right_var_state = var_state_from_numpy(data[offset: sampleLength - 1])

    # Compute AIC for each i using recursive variance
    minValue = 1e6
    minIndex = offset
    i = offset + 1
    while i < end:
        left_var_state = update_variance(left_var_state, data[i - 1])  # Expand left-side
        right_var_state = update_variance(right_var_state, data[i])  # Shrink right-side

        var_left = compute_variance(left_var_state) + epsilon
        var_right = compute_variance(right_var_state) + epsilon

        aicVal = i * np.log(var_left) + (sampleLength - i) * np.log(var_right)
        if (aicVal < minValue):
            minValue = aicVal
            minIndex = i
        i += 1

    return minIndex


@njit
def runOptimization(lagsForSequence):
    # Calculate the position estimate
    posEstimate = np.array([[widthD / 2], [heigthD / 2]])
    minNormRes = 1e6
    res = np.ascontiguousarray(np.empty((0, 0), dtype=np.float64))
    isValid = False
    validPosition = np.array([[100], [100]], dtype=np.float64)
    for i in range(len(lagsForSequence)):
        # for lag in lagsForSequence:
        lag = lagsForSequence[i]
        posEstimate = np.array([[widthD / 2], [heigthD / 2]])
        maxIter = 50
        y__1 = 0.0
        y__2 = 0.0
        y__3 = heigthD
        y__4 = heigthD
        for i in range(1, maxIter):
            J = getJacobian2d(posEstimate[0][0], posEstimate[1][0], y__1, y__2, y__3, y__4)
            res = getResidual2d(posEstimate[0][0], posEstimate[1][0], lag, y__1, y__2, y__3, y__4)
            # print(f"Residual: {res}")
            deltaPosition = np.linalg.inv((J.T @ J)) @ J.T @ res
            positionChangeLength = np.linalg.norm(deltaPosition)
            if (positionChangeLength > 0.02):
                deltaPosition = 0.02 / positionChangeLength * deltaPosition
            posEstimate = posEstimate - deltaPosition

            if (np.linalg.norm(deltaPosition) < 1e-4):
                break

            if (posEstimate[0][0] < 0) or (posEstimate[0][0] > widthD) or (posEstimate[1][0] < 0) or (posEstimate[1][0] > heigthD):
                break
            resPos = 0.005
            x_index = int(posEstimate[0][0] / resPos) + 1
            y_index = int(posEstimate[1][0] / resPos) + 1
            fak = 1.0
            y__1 = u_map[y_index, x_index] * fak
            y__2 = u2[y_index, x_index] * fak
            y__3 = heigthD - u3[y_index, x_index] * fak
            y__4 = heigthD - u4[y_index, x_index] * fak

        isInWindow = (posEstimate[0][0] > 0) and (posEstimate[0][0] < widthD) and (posEstimate[1][0] > 0) and (posEstimate[1][0] < heigthD)
        if (isInWindow):
            normResVec = np.linalg.norm(res)
            if (minNormRes > normResVec):
                isValid = True
                minNormRes = normResVec
                # print(f"Position estimate: {posEstimate}")
                validPosition = posEstimate

    return (isValid, validPosition, minNormRes)


def estimatePosition(data):
    ch1, ch2, ch3, ch4, frequency = data
    sos = scipy.signal.butter(8, 45000, 'low', fs=frequency, output='sos')
    # Filter
    dataFiltered = (scipy.signal.sosfilt(sos, ch1), scipy.signal.sosfilt(sos, ch2), scipy.signal.sosfilt(sos, ch3), scipy.signal.sosfilt(sos, ch4))

    offset = 20
    sampleLength = len(ch1)
    deltaTime = 1 / frequency
    searchWindow = int((1.5 * max(widthD, heigthD)) / (deltaTime * c))
    onsetIdx1 = getMinAic(dataFiltered[0], offset, sampleLength - offset - 1)
    offsetForFollowing = onsetIdx1 - searchWindow
    endForFollowing = onsetIdx1 + searchWindow
    if (endForFollowing > sampleLength or offsetForFollowing < 0):
        print("Data not considered due to onset position!")
        return (False, [100, 100], 1e6)

    onsetIdx2 = getMinAic(dataFiltered[1], offsetForFollowing, endForFollowing)
    onsetIdx3 = getMinAic(dataFiltered[2], offsetForFollowing, endForFollowing)
    onsetIdx4 = getMinAic(dataFiltered[3], offsetForFollowing, endForFollowing)
    onsetV = [onsetIdx1, onsetIdx2, onsetIdx3, onsetIdx4]

    # Stop here for too big diffs in onsets
    maxOnsettDiff = max(abs(x - y) for x, y in itertools.combinations(onsetV, 2))
    if (maxOnsettDiff >= searchWindow):
        print("Data not considered due to onset differences!")
        print(f"Max onset difference: {maxOnsettDiff}")
        return (False, [100, 100], 1e6)

    # Detect peaks in the area of the onset
    peakVectors = []
    peaksBefore = 1
    peaksAfter = 1
    for idx, onset in enumerate(onsetV):
        peakIdx, _ = find_peaks(dataFiltered[idx], distance=1, height=0.1, width=1)
        if len(peakIdx) == 0:
            break
        indices = extract_indices(peakIdx, onset, peaksBefore, peaksAfter)
        if len(indices) == 0:
            break
        peakVectors.append(indices)

    if len(peakVectors) < 4:
        # print("Data not considered due to missing peaks!")
        return (False, [100, 100], 1e6)

        # Get all possible combinations of peaks and calculate the time difference between them
    combinations = list(itertools.product(*peakVectors))
    lagsForSequence = []
    for combination in combinations:
        peakIndices = list(combination)
        if peakIndices:
            # channel order for 0 and 1 is reverserd in the adc conversion (it's 1 0 2 3)
            lagAic12 = (peakIndices[1] - peakIndices[0] + 0.25) * deltaTime  # + beacause channel 1 is sampled before 0
            lagAic13 = (peakIndices[2] - peakIndices[0] - 0.25) * deltaTime
            lagAic14 = (peakIndices[3] - peakIndices[0] - 0.5) * deltaTime
            lagAic23 = (peakIndices[2] - peakIndices[1] - 0.5) * deltaTime
            lagAic24 = (peakIndices[3] - peakIndices[1] - 0.75) * deltaTime
            lagAic34 = (peakIndices[3] - peakIndices[2] - 0.25) * deltaTime
            lagsForSequence.append(np.array([lagAic12, lagAic13, lagAic14, lagAic23, lagAic24, lagAic34], dtype=np.float64))

            # Calculate the position estimate
    return runOptimization(np.array(lagsForSequence, dtype=np.float64))



if sys.platform.startswith("linux"):
    import spidev
    import gpiod

    def receiver_process(queue, data_queue, stop_flag, plot, process, threshold):
        try:
            spi = spidev.SpiDev()
            spi.open(0, 0)
            spi.mode = MODE
            spi.bits_per_word = BITS_PER_WORD
            spi.max_speed_hz = SPI_SPEED

            # Restart uC
            with gpiod.request_lines(
                GPIO_CHIP,
                consumer="spi_interrupt_handler",
                config={GPIO_LINE_NRST: gpiod.LineSettings(
                    direction=gpiod.line.Direction.OUTPUT,
                    output_value=gpiod.line.Value.ACTIVE
                )}
            ) as request:
                request.set_value(GPIO_LINE_NRST, gpiod.line.Value.INACTIVE)
                time.sleep(0.1)
                request.set_value(GPIO_LINE_NRST, gpiod.line.Value.ACTIVE)

            tx_buf = [0] * (DATA_SIZE)
            tx_buf[0] = threshold & 0xFF
            tx_buf[1] = (threshold >> 8) & 0b11 
            with gpiod.request_lines(
                GPIO_CHIP,
                consumer="spi_interrupt_handler",
                config={GPIO_LINE_DATA_RDY: gpiod.LineSettings(
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
                                rx_buffer = spi.xfer3(tx_buf)
                                print(f"Received data from SPI {recCounter}")
                                data = np.array(rx_buffer, dtype=np.uint8).astype(np.uint16)
                                receivedData = ((data[1::2] << 8) | data[0::2]).astype(np.int16)
                                # Check the values to not be just zeros and espcially the channel mean values (0-3)
                                #if(np.any(receivedData[0:3] == 0) or (np.max(receivedData) == 0)):
                                #    print("Received invalid zero data")
                                #else:
                                ch1 = receivedData[4::4] - receivedData[0]
                                ch2 = receivedData[5::4] - receivedData[1]
                                ch3 = receivedData[6::4] - receivedData[2]
                                ch4 = receivedData[7::4] - receivedData[3]
                                # Only add to the plotting queue if the plot flag is set
                                if plot:
                                    queue.put((recCounter, ch1, ch2, ch3, ch4))
                                # Only add to the data processing queue if the process flag is set
                                if process:
                                    data_queue.put({
                                        'ch1': ch1,
                                        'ch2': ch2,
                                        'ch3': ch3,
                                        'ch4': ch4,
                                        'extras': None 
                                    })
                                recCounter += 1
        except Exception as e:
            print(f"Error in receiver_process: {e}")
        finally:
            spi.close()
            print("Receiver exiting...")

else:
    def receiver_process(queue, data_queue, stop_flag, plot, process, threshold):
        print("Running in non-Linux environment. Exiting receiver_process.")
        return

def cleanup(signum, frame):
    global stop_flag
    if not stop_flag.value:
        stop_flag.value = True
        print("\nCaught exit signal")

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
    sumAbsErrorX, sumErrorX = 0,0
    sumAbsErrorY, sumErrorY = 0,0
    maxErrorX , maxErrorY = -1,-1
    count = 0

    def analyze_batch(batch_data, batch_results, batch_id, extras = None):
        # Placeholder for batch analysis logic
        print(f"Analyzing batch {batch_id}")
        minRes = 1e6
        minPos = [100,100]
        for result in batch_results:
            isValid, positionEstimate, minNormRes = result
            if(isValid and (minRes > minNormRes)):
                minRes = minNormRes
                minPos = positionEstimate
                print(f"Candidate position estimate: {positionEstimate}")    
                print(f"Candidate normRes: {minNormRes}")  
        pos=[int((minPos[0]-0.005)/pixelw),int((minPos[1]-0.005)/pixelw)] 
        hmsysteme.put_pos(pos)
        hmsysteme.put_hit()

        print(f"Resulting position estimate:x {minPos[0]}, y: {minPos[1]} ")

        if extras:
            nonlocal sumAbsErrorX, sumAbsErrorY ,sumErrorX, sumErrorY, maxErrorX, maxErrorY, count
            xTrue = extras[0]
            yTrue = extras[1]
            errorX = minPos[0] - xTrue
            errorY = minPos[1] - yTrue
            if abs(errorX) > maxErrorX:
                maxErrorX = abs(errorX)
            if abs(errorY) > maxErrorY:
                maxErrorY = abs(errorY)
            sumErrorX += errorX
            sumErrorY += errorY
            sumAbsErrorX += abs(errorX)
            sumAbsErrorY += abs(errorY)
            count += 1
            print(f"Mean error x: {sumErrorX/count}, y: {sumErrorY/count}")
            print(f"Mean abs error x: {sumAbsErrorX/count}, y: {sumAbsErrorY/count}")
            print(f"Position error: x {errorX}, y {errorY}")
            print(f"Max error: x {maxErrorX}, y {maxErrorY}")

            
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
                data = copy.deepcopy(data_queue.get_nowait())
                ch1 = data['ch1']
                ch2 = data['ch2']
                ch3 = data['ch3']
                ch4 = data['ch4']
                factor = REF_VOLTAGE/np.power(2,BITS_PER_WORD)
                batch_data.append((ch1, ch2, ch3, ch4))

                # Start the batch timer if it's the first data in the batch
                if batch_start_time is None:
                    batch_start_time = time.time()

                # Submit the processing task to the thread pool and store the future
                future = executor.submit(estimatePosition, (ch1*factor, ch2*factor, ch3*factor, ch4*factor, FREQUENCY))
                processing_tasks.append(future)

            except QueueEmpty:
                # No new data arrived, check if a batch is ongoing and if it's time to finalize it
                if batch_start_time is not None and (time.time() - batch_start_time >= batch_duration):
                    # Wait for all processing tasks in the current batch to complete
                    batch_results = [future.result() for future in processing_tasks]

                    # Analyze the batch after all data has been processed
                    analyze_batch(batch_data, batch_results, batch_counter, data['extras'])
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
    pattern = r"x(\d+)_y(\d+)"
    match = re.search(pattern, npy_file)
    offsetx = -0.015
    offsety = -0.037
    xTrue = int(match.group(1))*0.001 + offsetx
    yTrue = int(match.group(2))*0.001 + offsety
    data = np.load(npy_file) 
    for item in data:
        ch1,ch2,ch3,ch4 = item
        data_queue.put({
                        'ch1': ch1,
                        'ch2': ch2,
                        'ch3': ch3,
                        'ch4': ch4,
                        'extras': (xTrue, yTrue)
                    })
    print("Data from npy file loaded into queue.")


def hardware_com_micro(threadname, debug_flag):
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    queue = multiprocessing.Queue(maxsize=100)  # Increased queue size
    data_queue = multiprocessing.Queue(maxsize=100)

    # Pass the plot and process flags to the receiver process
    receiver = multiprocessing.Process(target=receiver_process, args=(queue, data_queue, stop_flag, False, True, 700))
    
    processor = multiprocessing.Process(target=data_processing, args=(data_queue, stop_flag, False, True))

    receiver.start()
    processor.start()

    # If a file name is provided, load data
    if False:
        first = True
        path = "/home/micro/git/micro/hm01_micro_testreihen/diffMicro_17mmDistance"
        if os.path.isfile(path):
            if path.endswith('.npy'):
                load_and_enqueue_data(path, data_queue)
            else:
                print(f"{path} is a file but not a .npy file.")
        elif os.path.isdir(path):
            print(f"{path} is a directory. Scanning for .npy files...")
            for filename in os.listdir(path):
                if filename.endswith('.npy'):
                    full_path = os.path.join(path, filename)
                    print(f"Load {filename}")
                    load_and_enqueue_data(full_path,data_queue)
                    if first:
                        time.sleep(10.0)
                        first = False
                    else:
                        time.sleep(0.5)
                else:
                    print(f"{path} does not exist or is not accessible.")
        else:
            print(f"Error: File '{path}' not found.")
            exit(1)


    plotter_function(queue, stop_flag, False)

    receiver.join()
    processor.join()

    print("Ciao")


