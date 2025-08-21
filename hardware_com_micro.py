import signal
import sys
import numpy as np
import multiprocessing
import time
import argparse
from queue import Empty as QueueEmpty
from concurrent.futures import ThreadPoolExecutor
import os
from datetime import timedelta, datetime
import copy
import re
from positioning import PositionEstimator
import hmsysteme

# Constants
SPI_DEVICE = "/dev/spidev0.0"
GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE_DATA_RDY = 17
GPIO_LINE_NRST = 4
SPI_SPEED = 10000000 
BITS_PER_WORD = 8 
DATA_SIZE = 5980  # samples
SPI_MODE = 0
FREQUENCY = 500000 
REF_VOLTAGE = 3.3
FACTOR = REF_VOLTAGE / np.power(2, BITS_PER_WORD)

if sys.platform.startswith("linux"):
    import spidev
    import gpiod

    class ReceiverProcess(multiprocessing.Process):
        def __init__(self, plot_queue, data_queue, plot, process, threshold, mode):
            super().__init__()
            self.plot_queue = plot_queue
            self.data_queue = data_queue
            self.plot = plot
            self.process = process
            self.threshold = threshold
            self.mode = mode
            self.spi = None
            self.gpio_request = None

        def terminate(self):
            """Override terminate to clean up resources before termination."""
            try:
                if self.spi:
                    self.spi.close()
                    print("SPI connection closed during termination")
            except Exception as e:
                print(f"Error closing SPI during termination: {e}")
            
            # Call parent terminate
            super().terminate()

        def run(self):
            try:
                self.spi = spidev.SpiDev()
                self.spi.open(0, 0)
                self.spi.mode = SPI_MODE
                self.spi.bits_per_word = BITS_PER_WORD
                self.spi.max_speed_hz = SPI_SPEED
                print("Spi opened with mode {}, bits_per_word {}, max_speed_hz {}".format(
                    self.spi.mode, self.spi.bits_per_word, self.spi.max_speed_hz))
                
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
                print("GPIO Line Reset Done") 

                tx_buf = [0] * (DATA_SIZE)
                tx_buf[0] = self.threshold 
                if self.mode == 1:
                    tx_buf[1] = 1
                    
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
                    
                    while True:
                        if request.wait_edge_events(timedelta(seconds=1)):
                            events = request.read_edge_events()
                            for event in events:
                                if event.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
                                    rx_buffer = self.spi.xfer3(tx_buf)
                                    print(f"Received data from SPI {recCounter}")
                                    receivedData = np.array(rx_buffer, dtype=np.uint8).astype(np.int16)
                                    
                                    if(np.any(receivedData[0:3] == 0) or (np.max(receivedData) == 0)):
                                        print("Received invalid zero data")
                                    else:
                                        ch1 = (receivedData[4::4] - receivedData[0])*FACTOR
                                        ch2 = (receivedData[5::4] - receivedData[1])*FACTOR
                                        ch3 = (receivedData[6::4] - receivedData[2])*FACTOR
                                        ch4 = (receivedData[7::4] - receivedData[3])*FACTOR
                                        
                                        # Only add to the processing queue if the process flag is set
                                        if self.process:
                                            self.data_queue.put({
                                                'ch1': ch1,
                                                'ch2': ch2,
                                                'ch3': ch3,
                                                'ch4': ch4,
                                                'extras': None 
                                            })
                                        
                                        if self.plot:
                                            self.plot_queue.put((recCounter, ch1, ch2, ch3, ch4))
                                    recCounter += 1
                                    
                                    # Check periodically if we should exit
                                    try:
                                        # This will raise an exception if the process is terminated
                                        pass
                                    except:
                                        break
            except Exception as e:
                print(f"Error in receiver_process: {e}")
            finally:
                try:
                    if self.spi:
                        self.spi.close()
                except:
                    pass
                print("Receiver exiting...")

else:
    class ReceiverProcess(multiprocessing.Process):
        def __init__(self, plot_queue, data_queue, plot, process, threshold, mode):
            super().__init__()
            
        def terminate(self):
            """Override terminate for cleanup (no resources to clean in non-Linux)."""
            super().terminate()
            
        def run(self):
            print("Running in non-Linux environment. Exiting receiver_process.")
            return

class DataProcessingProcess(multiprocessing.Process):
    def __init__(self, data_queue, debug, process, positionEstimator):
        super().__init__()
        self.data_queue = data_queue
        self.debug = debug
        self.process = process
        self.positionEstimator = positionEstimator
        self.executor = None

    def terminate(self):
        """Override terminate to clean up thread pool."""
        try:
            if self.executor:
                self.executor.shutdown(wait=False)
                print("Thread pool shut down during termination")
        except Exception as e:
            print(f"Error shutting down thread pool: {e}")
        
        super().terminate()

    def run(self):
        if not self.process:
            print("Processing disabled. Exiting data_processing.")
            return

        batch_data = []  # Stores raw data for the batch
        batch_results = []  # Stores results from process_data for the batch
        batch_duration = 0.1  # 100ms in seconds
        batch_counter = 0
        batch_start_time = None
        processing_tasks = []  # Track processing tasks for the current batch
        sumAbsErrorX, sumErrorX = 0, 0
        sumAbsErrorY, sumErrorY = 0, 0
        maxErrorX, maxErrorY = -1, -1
        count = 0

        def analyze_batch(batch_data, batch_results, batch_id, extras=None):
            # Placeholder for batch analysis logic
            print(f"Analyzing batch {batch_id}")
            minRes = 1e6
            minPos = [100, 100]
            validResultContained = False
            for result in batch_results:
                isValid, positionEstimate, minNormRes = result
                if(isValid and (minRes > minNormRes)):
                    validResultContained = True
                    minRes = minNormRes
                    minPos = positionEstimate
                    print(f"Candidate position estimate: {positionEstimate}")    
                    print(f"Candidate normRes: {minNormRes}")
            if validResultContained:
                hmsysteme.hit_detected()
                hmsysteme.put_pos([minPos[0], minPos[1]])
                print(f"Resulting position estimate:x {minPos[0]}, y: {minPos[1]} ")
            else:
                print("No valid position estimate")

            if extras:
                nonlocal sumAbsErrorX, sumAbsErrorY, sumErrorX, sumErrorY, maxErrorX, maxErrorY, count
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

            if self.debug:
                # Ensure the directory exists
                os.makedirs("debug_data", exist_ok=True)
                # Add a timestamp to the filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"debug_data/batch_{batch_id}_{timestamp}.npy"
                np.save(filename, np.array(batch_data, dtype=np.int16))
                print(f"Saved batch {batch_id} to disk: {filename}")

        with ThreadPoolExecutor() as executor:
            self.executor = executor
            while True:
                try:
                    # Get data from the queue with a short timeout
                    data = copy.deepcopy(self.data_queue.get(timeout=0.1))
                    ch1 = data['ch1']
                    ch2 = data['ch2']
                    ch3 = data['ch3']
                    ch4 = data['ch4']
                    batch_data.append((ch1, ch2, ch3, ch4))

                    # Start the batch timer if it's the first data in the batch
                    if batch_start_time is None:
                        batch_start_time = time.time()

                    # Submit the processing task to the thread pool and store the future
                    future = self.executor.submit(self.positionEstimator.estimatePosition, (ch1, ch2, ch3, ch4, FREQUENCY))
                    processing_tasks.append(future)

                except QueueEmpty:
                    # No new data arrived, check if a batch is ongoing and if it's time to finalize it
                    if batch_start_time is not None and (time.time() - batch_start_time >= batch_duration):
                        # Wait for all processing tasks in the current batch to complete
                        batch_results = [future.result() for future in processing_tasks]

                        # Analyze the batch after all data has been processed
                        if batch_data:  # Only analyze if we have data
                            last_data = batch_data[-1] if hasattr(self, '_last_data_extras') else None
                            analyze_batch(batch_data, batch_results, batch_counter, 
                                        getattr(self, '_last_data_extras', None))
                        
                        batch_data = []  # Reset the batch data
                        batch_results = []  # Reset the batch results
                        processing_tasks = []  # Reset the processing tasks
                        batch_counter += 1
                        batch_start_time = None  # Reset the batch timer
                except Exception as e:
                    print(f"Error in data processing: {e}")
                    continue

        # Ensure any remaining data in the batch is processed and analyzed before exiting
        if batch_data and processing_tasks:
            # Wait for all processing tasks in the current batch to complete
            batch_results = [future.result() for future in processing_tasks]
            # Analyze the final batch
            analyze_batch(batch_data, batch_results, batch_counter, 
                        getattr(self, '_last_data_extras', None))
        
        # Clean up executor reference
        self.executor = None
        print("Data Processing exiting...")

class PlotterProcess(multiprocessing.Process):
    def __init__(self, plot_queue, plot):
        super().__init__()
        self.plot_queue = plot_queue
        self.plot = plot

    def terminate(self):
        """Override terminate to clean up matplotlib resources."""
        try:
            # Try to close any open matplotlib figures
            import matplotlib.pyplot as plt
            plt.close('all')
            print("Matplotlib figures closed during termination")
        except Exception as e:
            print(f"Error closing matplotlib figures: {e}")
        
        super().terminate()

    def run(self):
        """ Listens for data and plots it in the main thread. """
        if not self.plot:
            return

        # Import matplotlib here to avoid issues with multiprocessing
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        
        plt.ion()  # Turn on interactive mode
        figures = []  # Store references to figures to keep them alive

        while not self.plot_queue.empty() or True:
            try:
                # Get data from the plot_queue (non-blocking)
                try:
                    recCounter, ch1, ch2, ch3, ch4 = self.plot_queue.get(timeout=0.1)
                except QueueEmpty:
                    # No data in the plot_queue, continue to process events
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
            except Exception as e:
                print(f"Error in plotter: {e}")
                continue

        print("Plotter exiting...")

def load_and_enqueue_data(npy_file, data_queue, plot_queue, plot):
    pattern = r"x(\d+)_y(\d+)"
    match = re.search(pattern, npy_file)
    offsetx = -0.015
    offsety = -0.037
    offsetx = 0
    offsety = 0
    xTrue = int(match.group(1))*0.001 + offsetx
    yTrue = int(match.group(2))*0.001 + offsety
    data = np.load(npy_file) 
    for item in data:
        ch1, ch2, ch3, ch4 = item
        data_queue.put({
                        'ch1': -ch1,
                        'ch2': -ch2,
                        'ch3': -ch3,
                        'ch4': -ch4,
                        'extras': (xTrue, yTrue)
                    })
        if plot: 
            plot_queue.put((0, ch1, ch2, ch3, ch4))
    print("Data from npy file loaded into plot_queue.")

def start(plot=False, process=True, debug=False, filename="", threshold=200, mode=1):
    """
    Start the SPI data processing system non-blocking.
    
    Returns:
        All processes implement multiprocessing.Process and can be terminated with .terminate()
    """
    plot_queue = multiprocessing.Queue(maxsize=100)
    data_queue = multiprocessing.Queue(maxsize=100)

    positionEstimator = PositionEstimator(.370, .215, mode)

    # Create process instances
    print(f"Starting sampleboard in mode: {mode} and threshold {threshold}")
    
    receiver = ReceiverProcess(plot_queue, data_queue, plot, process, threshold, mode)
    processor = DataProcessingProcess(data_queue, debug, process, positionEstimator)
    plotter = PlotterProcess(plot_queue, plot) if plot else None

    # Start processes
    receiver.start()
    processor.start()
    if plotter:
        plotter.start()

    # If a file name is provided, load data
    if filename:
        first = True
        path = filename
        if os.path.isfile(path):
            if path.endswith('.npy'):
                load_and_enqueue_data(path, data_queue, plot_queue, plot)
            else:
                print(f"{path} is a file but not a .npy file.")
        elif os.path.isdir(path):
            print(f"{path} is a directory. Scanning for .npy files...")
            for filename in os.listdir(path):
                if filename.endswith('.npy'):
                    full_path = os.path.join(path, filename)
                    load_and_enqueue_data(full_path, data_queue, plot_queue, plot)
                    if first:
                        time.sleep(45.0)
                        first = False
                    else:
                        time.sleep(0.5)
        else:
            print(f"Error: File '{filename}' not found.")
            return None

    return receiver, processor, plotter

def stop_processes(*processes):
    """
    Utility function to stop all processes gracefully.
    """
    # Terminate processes
    for process in processes:
        if process and process.is_alive():
            process.terminate()
    
    # Wait for processes to finish
    for process in processes:
        if process:
            process.join(timeout=2)
            if process.is_alive():
                # Force kill if still alive
                process.kill() if hasattr(process, 'kill') else None

def main():
    parser = argparse.ArgumentParser(description="SPI Data Processing")
    parser.add_argument("-p", action="store_true", help="Enable plotting")
    parser.add_argument("-r", action="store_true", help="Enable processing")
    parser.add_argument("-d", action="store_true", help="Enable debug mode (save batch data to disk)")
    parser.add_argument("-f", type=str, default="", help="File name to load data from (optional)")
    parser.add_argument("-t", type=int, default=200, choices=range(10, 255), help="Threshold value. Below 128 will check for minima, above for maxima (default: 200, min: 10, max: 255)")
    parser.add_argument("-m", type=int, default=0, choices=range(0, 2), help="Mode 0 for unfiltered threshold, Mode 1 for filtered threshold")
    args = parser.parse_args()

    def cleanup(signum, frame):
        print("\nCaught exit signal")
        stop_processes(receiver, processor, plotter)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Start the processes (non-blocking)
    result = start(args.p, args.r, args.d, args.f, args.t, args.m, return_queues=False)
    if result is None:
        sys.exit(1)
        
    receiver, processor, plotter = result

    try:
        # Keep the main thread alive
        while True:
            # Check if processes are still alive
            if not receiver.is_alive() and not processor.is_alive():
                print("All processes have terminated")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        stop_processes(receiver, processor, plotter)

    print("Ciao")

if __name__ == "__main__":
    main()