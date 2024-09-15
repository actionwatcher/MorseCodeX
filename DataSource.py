import random
from helpers import log

class DataSource:
    def __init__(self, file_path='MASTER.SCP', num_words=50, pre_message=False, rst=False, serial=False, challenges={}, challenge_frac=0.25):
        self.num_challenges = min(int(round(challenge_frac * num_words)), len(challenges))
        self.num_words = num_words - self.num_challenges
        self.rst = '5nn ' if rst else ''
        self.pre_msgs_selection = []
        self.pre_msgs = []
        self.serial_numbers = []
        if pre_message:
            self.pre_msgs_selection = ('tu ,'*20+','*8+'r ,'*4+'qsl ,'+'ur ,'*3).split(',')
        self.generate_sernum = serial
        self.msgs = self._load_words(file_path)
        self.challenge_list = list(challenges.keys())
        self.challenge_freq = [ max(1, val) for val in challenges.values()] # chance is proportional to number of erros
                                                                            # 0 will not include value so replace 0s with 1
        self.reset()
        
    def _load_words(self, file_path):
        words = []
        format_spec = None
        default_names = ['Joe', 'John', 'Nick', 'Mike', 'Geo'] #in case if no name yet present in the dictionalry
        try:
            ser_num=''
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
                                word_dict['Name'] = random.choice(default_names)
                            elif word_dict['Name'] not in default_names:
                                default_names.append(word_dict['Name'])

                            combined_string = ' '.join(
                                word_dict[field] for field in format_spec if field not in ('Call', 'UserText')
                            )
                            if self.generate_sernum:
                                ser_num = str(random.randint(1, 1300)) + ' '
                                if random.choice([0, 1, 2]) == 0: # in 1/3 cases
                                    ser_num = ser_num.replace('1', 'a').replace('9', 'n').replace('0', 't')
                                else: # zero fill
                                    while(len(ser_num)<4):
                                        ser_num = 't' + ser_num
                                self.serial_numbers.append(ser_num)
                            words.append(combined_string)
                        else:
                            words.append(line)
        except FileNotFoundError:
            log("error", f"File {file_path} not found.")
        return words
    
    def reset(self):
        if self.num_words <= len(self.msgs):  # Prefer unique selection
            self.selected_msgs = random.sample(self.msgs, k=self.num_words)
        else:
            self.selected_msgs = random.choices(self.msgs, k=self.num_words)
        
        if len(self.challenge_list) and self.num_challenges:
            selected_challenges = random.sample(self.challenge_list, k=self.num_challenges)
            self.selected_msgs.extend(selected_challenges)
            random.shuffle(self.selected_msgs)

        if self.pre_msgs_selection:
            self.pre_msgs = random.choices(self.pre_msgs_selection, k=(self.num_words + self.num_challenges))
        else:
            self.pre_msgs = ['' for _ in range(self.num_words + self.num_challenges)]
        self.index = 0

    def get_next_word(self):
        if self.index >= len(self.selected_msgs):
            self.index = 0
            return (None, None, None, None)
        msg = self.selected_msgs[self.index]
        pre_msg = self.pre_msgs[self.index]
        ser_num = self.serial_numbers[self.index] if self.serial_numbers else ''
        self.index += 1
        return (pre_msg, self.rst, ser_num, msg)

if __name__ == '__main__':
    data_source = DataSource(file_path='MASTER.SCP', num_words=10)
    print('Testing super-check partial file with MASTER.SCP')
    for _ in range(5):
        print(data_source.get_next_word())
    
    data_source = DataSource(file_path='NAQPCW.txt', num_words=10, pre_message=True)
    print('Testing super-check partial file with NAQPCW.txt')
    for _ in range(5):
        print(data_source.get_next_word())


    data_source = DataSource(file_path='NAQPCW.txt', num_words=10, pre_message=True, serial=True)
    print('Testing super-check partial file with NAQPCW.txt')
    for _ in range(5):
        print(data_source.get_next_word())
