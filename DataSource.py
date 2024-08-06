import random

class DataSource:
    def __init__(self, file_path='MASTER.SCP', num_words=50, pre_message=False):
        self.names = []  # List to store encountered names
        self.num_words = num_words
        self.pre_msgs_selection = []
        self.pre_msgs = []
        if pre_message:
            self.pre_msgs_selection = ('tu ,'*20+','*8+'r ,'*4+'qsl ,'+'ur ,'+'5nn ').split(',')
        self.msgs = self._load_words(file_path)
        self.reset()

    def _load_words(self, file_path):
        words = []
        format_spec = None
        default_names = ['Joe', 'John', 'Nick', 'Mike', 'Geo'] #in case if no name yet present in the dictionalry
        try:
            pre_msg = ''
            with open(file_path, 'r') as file:
                for line_number, line in enumerate(file):
                    line = line.strip()
                    if line_number == 0 and line.startswith('!!Order!!'):
                        format_spec = [field.strip() for field in line.split('!!Order!!')[1].split(',') if field.strip()]
                    elif line and not line.startswith('#'):
                        if self.pre_msgs_selection:
                            pre_msg = random.choice(self.pre_msgs_selection)
                        self.pre_msgs.append(pre_msg)
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
        if self.num_words <= len(self.msgs):  # Prefer unique selection
            self.selected_msgs = random.sample(self.msgs, k=self.num_words)
        else:
            self.selected_msgs = random.choices(self.msgs, k=self.num_words)
        self.index = 0

    def get_next_word(self):
        if self.index >= len(self.selected_msgs):
            self.index = 0
            return (None, None)
        msg = self.selected_msgs[self.index]
        pre_msg = self.pre_msgs[self.index]
        self.index += 1
        return (pre_msg, msg)

if __name__ == '__main__':
    data_source = DataSource(file_path='MASTER.SCP', num_words=10)
    print('Testing super-check partial file with MASTER.SCP')
    for _ in range(5):
        print(data_source.get_next_word())
    
    data_source = DataSource(file_path='NAQPCW.txt', num_words=10, pre_message=True)
    print('Testing super-check partial file with NAQPCW.txt')
    for _ in range(5):
        print(data_source.get_next_word())
