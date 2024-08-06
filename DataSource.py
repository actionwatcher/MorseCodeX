import random

class DataSource:
    def __init__(self, file_path='MASTER.SCP', num_words=50):
        self.names = []  # List to store encountered names
        self.words = self._load_words(file_path)
        self.num_words = num_words
        self.reset()

    def _load_words(self, file_path):
        words = []
        format_spec = None
        default_names = ['Joe', 'John', 'Nick', 'Mike', 'Geo']
        try:
            with open(file_path, 'r') as file:
                for line_number, line in enumerate(file):
                    line = line.strip()
                    if line_number == 0 and line.startswith('!!Order!!'):
                        format_spec = [field.strip() for field in line.split('!!Order!!')[1].split(',') if field.strip()]
                    elif line and not line.startswith('#'):
                        if format_spec:
                            fields = line.split(',')
                            if len(fields) < len(format_spec):
                                fields.extend([''] * (len(format_spec) - len(fields)))
                            word_dict = {key: value for key, value in zip(format_spec, fields)}

                            # Handling empty Name field (empty string '')
                            if 'Name' in word_dict and word_dict['Name'] == '':
                                if self.names:
                                    word_dict['Name'] = random.choice(self.names)
                                else:
                                    word_dict['Name'] = random.choice(default_names)
                            
                            # Add the Name to the list if not empty
                            if word_dict['Name']:
                                self.names.append(word_dict['Name'])

                            combined_string = ' '.join(
                                word_dict[field] for field in format_spec if field not in ('Call', 'UserText')
                            )
                            words.append(combined_string)
                        else:
                            words.append(line)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        return words
    
    def reset(self):
        if self.num_words <= len(self.words):  # Prefer unique selection
            self.selected_words = random.sample(self.words, k=self.num_words)
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

if __name__ == '__main__':
    data_source = DataSource(file_path='MASTER.SCP', num_words=10)
    print('Testing super-check partial file with MASTER.SCP')
    for _ in range(5):
        print(data_source.get_next_word())
    
    data_source = DataSource(file_path='NAQPCW.txt', num_words=10)
    print('Testing super-check partial file with NAQPCW.txt')
    for _ in range(5):
        print(data_source.get_next_word())
