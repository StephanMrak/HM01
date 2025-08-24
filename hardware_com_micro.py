import signal
import sys
import multiprocessing
import time
import argparse
import os
import hmsysteme

# Only keep essential constants in parent process
SPI_DEVICE = "/dev/spidev0.0"
GPIO_CHIP = "/dev/gpiochip0"
GPIO_LINE_DATA_RDY = 17
GPIO_LINE_NRST = 4
SPI_SPEED = 10000000 
BITS_PER_WORD = 8 
DATA_SIZE = 5980
SPI_MODE = 0
FREQUENCY = 500000 
REF_VOLTAGE = 3.3

# Global developer data queue - simple addition for data sharing
developer_data_queue = None

class ReceiverProcess(multiprocessing.Process):
        def __init__(self, plot_queue, plot, threshold, mode, debug, dev_queue=None):
            super().__init__()
            self.plot_queue = plot_queue
            self.plot = plot
            self.threshold = threshold
            self.mode = mode
            self.debug = debug
            self.spi = None
            self.gpio_request = None
            self.dev_queue = dev_queue  # Add developer data queue
            
            # Import heavy libraries in __init__ to avoid import overhead during processing
            import numpy as np
            from positioning import PositionEstimator
            from datetime import timedelta, datetime
            import re
            
            # Store imported modules as instance variables for fast access
            self.np = np
            self.datetime = datetime
            self.re = re
            
            # Calculate factor once
            self.FACTOR = REF_VOLTAGE / np.power(2, BITS_PER_WORD)
            
            # Create PositionEstimator in __init__ for faster access
            self.positionEstimator = PositionEstimator(.370, .215, mode)
            
            # Statistics tracking
            self.sumAbsErrorX = 0
            self.sumAbsErrorY = 0
            self.sumErrorX = 0
            self.sumErrorY = 0
            self.maxErrorX = -1
            self.maxErrorY = -1
            self.count = 0

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

        def process_data_immediately(self, ch1, ch2, ch3, ch4, extras=None):
            """Process data immediately after receiving it - optimized for speed"""
            try:
                # All imports are already done in __init__, use instance variables for speed
                # Process the data to get position estimate
                isValid, positionEstimate, minNormRes = self.positionEstimator.estimatePosition((ch1, ch2, ch3, ch4, FREQUENCY))
                
                # NEW: Send developer data to queue if enabled
                if self.dev_queue is not None:
                    try:
                        dev_data = {
                            'timestamp': time.time(),
                            'ch1': ch1.tolist(),
                            'ch2': ch2.tolist(),
                            'ch3': ch3.tolist(),
                            'ch4': ch4.tolist(),
                            'position_valid': bool(isValid),
                            'position_x': float(positionEstimate[0]) if isValid else None,
                            'position_y': float(positionEstimate[1]) if isValid else None,
                            'residual': float(minNormRes) if isValid else None
                        }
                        # Non-blocking put to avoid slowdown
                        if not self.dev_queue.full():
                            self.dev_queue.put_nowait(dev_data)
                    except:
                        pass  # Don't let developer logging interfere with main functionality
                
                if isValid:
                    d_lenght = 0.341
                    factor = 0.97
                    pixelw = hmsysteme.get_size()[0] / d_lenght * factor
                    pos=[int((positionEstimate[0]-0.01)*pixelw),int((positionEstimate[1]-0.0125)*pixelw)] 
                    hmsysteme.put_pos(pos)
                    #time.sleep(.5)
                    hmsysteme.put_hit()
                    print(f"Hit detected at position: x {float(positionEstimate[0]):.3f}, y: {float(positionEstimate[1]):.3f}, residual: {float(minNormRes):.6f}")
                    
                    # Handle debug statistics if extras data is provided
                    if extras:
                        xTrue, yTrue = extras
                        errorX = positionEstimate[0] - xTrue
                        errorY = positionEstimate[1] - yTrue
                        
                        if abs(errorX) > self.maxErrorX:
                            self.maxErrorX = abs(errorX)
                        if abs(errorY) > self.maxErrorY:
                            self.maxErrorY = abs(errorY)
                        
                        self.sumErrorX += errorX
                        self.sumErrorY += errorY
                        self.sumAbsErrorX += abs(errorX)
                        self.sumAbsErrorY += abs(errorY)
                        self.count += 1
                        
                        print(f"Mean error x: {float(self.sumErrorX/self.count):.3f}, y: {float(self.sumErrorY/self.count):.3f}")
                        print(f"Mean abs error x: {float(self.sumAbsErrorX/self.count):.3f}, y: {float(self.sumAbsErrorY/self.count):.3f}")
                        print(f"Position error: x {float(errorX):.3f}, y {float(errorY):.3f}")
                        print(f"Max error: x {float(self.maxErrorX):.3f}, y {float(self.maxErrorY):.3f}")
                else:
                    print("No valid position estimate")
                    
                # Save debug data if enabled
                if self.debug:
                    os.makedirs("debug_data", exist_ok=True)
                    timestamp = self.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    filename = f"debug_data/shot_{timestamp}.npy"
                    self.np.save(filename, self.np.array([(ch1, ch2, ch3, ch4)], dtype=self.np.float32))
                    print(f"Saved shot data to disk: {filename}")
                    
            except Exception as e:
                print(f"Error processing data: {e}")

        def run(self):
            # Import only SPI-specific libraries in run()
            if sys.platform.startswith("linux"):
                import spidev
                import gpiod
                from datetime import timedelta
            else:
                print("Running in non-Linux environment. Exiting receiver_process.")
                return
            
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
                
                tx_buf[1] =self.mode 
                    
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
                                    receivedData = self.np.array(rx_buffer, dtype=self.np.uint8).astype(self.np.int16)
                                    
                                    if not (self.np.any(receivedData[0:3] == 0) or (self.np.max(receivedData) == 0)):
                                        ch1 = (receivedData[4::4] - receivedData[0]) * self.FACTOR
                                        ch2 = (receivedData[5::4] - receivedData[1]) * self.FACTOR
                                        ch3 = (receivedData[6::4] - receivedData[2]) * self.FACTOR
                                        ch4 = (receivedData[7::4] - receivedData[3]) * self.FACTOR
                                        
                                        # Process data immediately
                                        self.process_data_immediately(ch1, ch2, ch3, ch4)
                                        
                                        # Add to plot queue if plotting is enabled
                                        if self.plot:
                                            self.plot_queue.put((recCounter, ch1, ch2, ch3, ch4))
                                    else:
                                        print("Received invalid zero data")
                                    
                                    recCounter += 1
            except Exception as e:
                print(f"Error in receiver_process: {e}")
            finally:
                try:
                    if self.spi:
                        self.spi.close()
                except:
                    pass
                print("Receiver exiting...")

class NonLinuxReceiverProcess(multiprocessing.Process):
    def __init__(self, plot_queue, plot, threshold, mode, debug, dev_queue=None):
        super().__init__()
        
    def terminate(self):
        """Override terminate for cleanup (no resources to clean in non-Linux)."""
        super().terminate()
        
    def run(self):
        print("Running in non-Linux environment. Exiting receiver_process.")
        return

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

        # Import matplotlib here to avoid issues with multiprocessing and reduce parent memory
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        from queue import Empty as QueueEmpty
        
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

def load_and_enqueue_data(npy_file, receiver_process, plot_queue, plot):
    """Load data from file and process it directly through the receiver"""
    import numpy as np  # Import numpy only when needed
    import re
    
    pattern = r"x(\d+)_y(\d+)"
    match = re.search(pattern, npy_file)
    offsetx = 0
    offsety = 0
    if match:
        xTrue = int(match.group(1))*0.001 + offsetx
        yTrue = int(match.group(2))*0.001 + offsety
    else:
        xTrue, yTrue = 0, 0
        
    data = np.load(npy_file) 
    for item in data:
        ch1, ch2, ch3, ch4 = item
        
        # Process data directly
        receiver_process.process_data_immediately(ch1, ch2, ch3, ch4, None if not match else (xTrue,yTrue))
        
        # Add to plot queue if plotting
        if plot: 
            plot_queue.put((0, ch1, ch2, ch3, ch4))
            
    print(f"Data from {npy_file} processed directly.")

def start(plot=False, process=True, debug=False, filename="", threshold=200, mode=1, enable_developer=False):
    """
    Start the SPI data processing system non-blocking.
    
    Returns:
        Processes that can be terminated with .terminate()
    """
    global developer_data_queue
    
    plot_queue = multiprocessing.Queue(maxsize=10) if plot else None  # Reduced from 100

    # NEW: Create developer data queue if enabled
    if enable_developer:
        developer_data_queue = multiprocessing.Queue(maxsize=10)  # Keep last 10 frames
    else:
        developer_data_queue = None

    # Create process instances
    print(f"Starting sampleboard in mode: {mode} and threshold {threshold}")
    
    if sys.platform.startswith("linux"):
        receiver = ReceiverProcess(plot_queue, plot, threshold, mode, debug, developer_data_queue)
    else:
        receiver = NonLinuxReceiverProcess(plot_queue, plot, threshold, mode, debug, developer_data_queue)
    plotter = PlotterProcess(plot_queue, plot) if plot else None

    # Start processes
    if process:
        receiver.start()
    if plotter:
        plotter.start()

    # If a file name is provided, load data
    if filename:
        first = True
        path = filename
        if os.path.isfile(path):
            if path.endswith('.npy'):
                load_and_enqueue_data(path, receiver, plot_queue, plot)
            else:
                print(f"{path} is a file but not a .npy file.")
        elif os.path.isdir(path):
            print(f"{path} is a directory. Scanning for .npy files...")
            for filename in os.listdir(path):
                if filename.endswith('.npy'):
                    full_path = os.path.join(path, filename)
                    load_and_enqueue_data(full_path, receiver, plot_queue, plot)
                    if first:
                        time.sleep(45.0)
                        first = False
                    else:
                        time.sleep(0.5)
        else:
            print(f"Error: File '{filename}' not found.")
            return None

    return receiver, None, plotter  # Return None for the removed processor

def get_developer_data():
    """Get developer data from the queue - NEW function for webserver"""
    global developer_data_queue
    if developer_data_queue is None:
        return []
    
    data_frames = []
    try:
        # Get all available data (up to 10 items)
        while not developer_data_queue.empty() and len(data_frames) < 10:
            data_frames.append(developer_data_queue.get_nowait())
    except:
        pass
    
    return data_frames

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
    parser.add_argument("-d", action="store_true", help="Enable debug mode (save shot data to disk)")
    parser.add_argument("-f", type=str, default="", help="File name to load data from (optional)")
    parser.add_argument("-t", type=int, default=200, choices=range(10, 255), help="Threshold value. Below 128 will check for minima, above for maxima (default: 200, min: 10, max: 255)")
    parser.add_argument("-m", type=int, default=0, choices=range(0, 2), help="Mode 0 for unfiltered threshold, Mode 1 for filtered threshold")
    parser.add_argument("--dev", action="store_true", help="Enable developer data logging")
    args = parser.parse_args()

    def cleanup(signum, frame):
        print("\nCaught exit signal")
        stop_processes(receiver, processor, plotter)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Start the processes (non-blocking)
    result = start(args.p, args.r, args.d, args.f, args.t, args.m, args.dev)
    if result is None:
        sys.exit(1)
        
    receiver, processor, plotter = result

    try:
        # Keep the main thread alive
        while True:
            # Check if receiver process is still alive
            if not receiver.is_alive():
                print("Receiver process has terminated")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        stop_processes(receiver, processor, plotter)

    print("Ciao")

if __name__ == "__main__":
    main()
