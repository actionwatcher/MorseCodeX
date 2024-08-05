import random

class DataSource:
    def __init__(self, file_path='MASTER.SCP', num_words=50):
        self.words = self._load_words(file_path)
        self.num_words = num_words
        self.reset()

    def _load_words(self, file_path):
        words = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        words.append(line)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        return words
    
    def reset(self):
        if self.num_words <= len(self.words): # pefer unique selection
            self.selected_words = random.sample(self.words, k = self.num_words)
        else:
            self.selected_words = random.choices(self.words, k=self.num_words)
        self.index = 0

    def get_next_word(self):
        if self.index >= len(self.selected_words):
            self.index = 0
            return None
        word = self.selected_words[self.index]
        self.index += 1
        return word

# Example usage
# data_source = DataSource(file_path='MASTER.SCP', num_words=10)
# print(data_source.get_next_word())
