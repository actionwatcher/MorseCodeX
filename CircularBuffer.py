import numpy as np
import threading

class CircularBuffer:
    def __init__(self, size, dtype=np.float32):
        self.buffer = np.zeros(size, dtype=dtype)
        self.size = size
        self.start = 0
        self.end = 0
        self.count = 0
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)

    def put(self, data):
        data_length = len(data)
        while data_length > 0:
            with self.not_full:
                while self.count == self.size:
                    self.not_full.wait()
                space_available = self.size - self.count
                chunk_size = min(space_available, data_length)

                end_index = (self.start + self.count) % self.size
                if end_index + chunk_size <= self.size:
                    self.buffer[end_index:end_index + chunk_size] = data[:chunk_size]
                else:
                    part1_size = self.size - end_index
                    self.buffer[end_index:] = data[:part1_size]
                    self.buffer[:chunk_size - part1_size] = data[part1_size:chunk_size]

                self.count += chunk_size
                data = data[chunk_size:]
                data_length -= chunk_size

                self.not_empty.notify_all()

    def get(self, array_size):
        with self.not_empty:
            success = self.not_empty.wait_for(lambda : self.count, timeout=0.01)
            data = np.zeros(array_size, dtype=self.buffer.dtype) #fill with zerros
            if not success:
                return data
            
            actual_size = min(array_size, self.count)
            start_index = self.start

            if start_index + actual_size <= self.size:
                data[:actual_size] = self.buffer[start_index:start_index + actual_size]
            else:
                part1_size = self.size - start_index
                data[:part1_size] = self.buffer[start_index:]
                data[part1_size:] = self.buffer[:actual_size - part1_size]

            self.start = (self.start + actual_size) % self.size
            self.count -= actual_size

            self.not_full.notify_all()
            return data

    def is_full(self):
        with self.lock:
            return self.count == self.size

    def is_empty(self):
        with self.lock:
            return self.count == 0


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
