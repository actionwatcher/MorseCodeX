import queue
import threading
import numpy as np
import time

class CircularBuffer:
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize)
        self.maxsize = maxsize
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)

    def put(self, data):
        with self.not_full:
            while self.queue.qsize() >= self.maxsize:
                self.not_full.wait()
            self.queue.put((0, data))  # Always add the tuple (0, data)
            self.not_empty.notify()

    def get(self, chunk_size):
        result = np.zeros(chunk_size, dtype=int)
        filled = 0
        
        with self.not_empty:
            while filled < chunk_size:
                while self.queue.qsize() == 0:
                    self.not_empty.wait()
                
                start_idx, data = self.queue.get()
                self.not_full.notify()
                
                remaining = len(data) - start_idx
                if remaining >= chunk_size - filled:
                    result[filled:filled + chunk_size - filled] = data[start_idx:start_idx + chunk_size - filled]
                    # Put the remaining part back into the queue if any
                    if remaining > chunk_size - filled:
                        self.queue.put((start_idx + chunk_size - filled, data))
                    filled = chunk_size
                else:
                    result[filled:filled + remaining] = data[start_idx:]
                    filled += remaining

        return result

    def peek(self):
        with self.queue.mutex:
            if self.queue.qsize() > 0:
                return self.queue.queue[0]
            else:
                raise queue.Empty

# Corrected producer function
def producer(buffer, N, chunk_size, error_flag):
    i = 0
    while i < N:
        if error_flag.is_set():
            break
        # Generate an array with length between 1 and the smaller of chunk_size or remaining numbers
        remaining = N - i
        length = min(np.random.randint(1, chunk_size + 1), remaining)
        data = np.arange(i, i + length)
        buffer.put(data)
        i += length

def consumer(buffer, N, chunk_size, error_flag):
    current_index = 0
    while current_index < N:
        if error_flag.is_set():
            break
        data = buffer.get(chunk_size)
        expected_chunk = np.arange(current_index, current_index + len(data))
        if not np.array_equal(data, expected_chunk):
            print(f"Test failed! Expected chunk: {expected_chunk}, Failed chunk: {data}")
            error_flag.set()
            return
        current_index += len(data)

def monitor_buffer(buffer, stop_event):
    while not stop_event.is_set():
        time.sleep(1)
        with buffer.lock:
            print(f"Buffer count: {buffer.queue.qsize()}")


if __name__ == "__main__":
    import time

    # Testing part
    N = 100000
    L = 3000  # Set the maximum value for chunk_size
    K = 5   # Number of iterations
    buffer_size = 100  # Adjust buffer size as needed

    # Function to simulate concurrent writes
    def producer(buffer, N, chunk_size, error_flag):
        i = 0
        while i < N:
            if error_flag.is_set():
                break
            # Generate an array with length between 1 and the smaller of chunk_size or remaining numbers
            remaining = N - i
            length = min(np.random.randint(1, chunk_size + 1), remaining)
            data = np.arange(i, i + length)
            buffer.put(data)
            i += length

    def consumer(buffer, N, chunk_size, error_flag):
        current_index = 0
        
        while current_index < N:
            if error_flag.is_set():
                break
            
            data = buffer.get(chunk_size)
            expected_chunk = np.arange(current_index, current_index + len(data))
            
            if not np.array_equal(data, expected_chunk):
                print(f"Test failed! Expected chunk: {expected_chunk}, Failed chunk: {data}")
                error_flag.set()
                return
            
            current_index += len(data)

    def monitor_buffer(buffer, stop_event):
        while not stop_event.is_set():
            time.sleep(3)
            print(f"Buffer count: {buffer.count}")

    chunk_sizes = np.linspace(1, L, K, dtype=int)

    for chunk_size in chunk_sizes:
        print(f"Running test with chunk_size = {chunk_size}")
        start_time = time.time()
        circular_buffer = CircularBuffer(buffer_size)
        error_flag = threading.Event()
        #stop_event = threading.Event()

        # Create threads
        producer_thread = threading.Thread(target=producer, args=(circular_buffer, N, chunk_size, error_flag))
        consumer_thread = threading.Thread(target=consumer, args=(circular_buffer, N, max(1, chunk_size//2), error_flag))
        #monitor_thread = threading.Thread(target=monitor_buffer, args=(circular_buffer, stop_event))

        # Start threads
        producer_thread.start()
        consumer_thread.start()
        #monitor_thread.start()

        # Wait for threads to finish
        producer_thread.join()
        consumer_thread.join()

        # Stop the monitor thread
        #stop_event.set()
        #monitor_thread.join()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Test with chunk_size = {chunk_size} completed in {elapsed_time:.2f} seconds")

        if not error_flag.is_set():
            print(f"Test completed successfully with chunk_size = {chunk_size}.")
        else:
            print(f"Test failed with chunk_size = {chunk_size}.")
            break
