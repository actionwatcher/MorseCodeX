import random
import os
from helpers import log
import helpers

class DataSource:
    def __init__(self, file_path='MASTER.SCP', num_words=50, policies_file = 'message_policies.json', pre_message=False, rst=False, serial=False, challenges={}, challenge_frac=0.25):
        self.num_challenges = min(int(round(challenge_frac * num_words)), len(challenges))
        self.num_words = num_words - self.num_challenges
        self.rst = '5nn ' if rst else ''
        self.pre_msgs_selection = []
        self.pre_msgs = []
        self.serial_numbers = []
        if pre_message:
            self.pre_msgs_selection = ('tu ,'*20+','*8+'r ,'*4+'qsl ,'+'ur ,'*3).split(',')
        self.generate_sernum = serial
        self.policies = helpers.load_json(policies_file)
        self.msgs = self._load_words(file_path)
        self.challenge_list = list(challenges.keys())
        self.challenge_freq = [ max(1, val) for val in challenges.values()] # chance is proportional to number of erros
                                                                            # 0 will not include value so replace 0s with 1
        
        self.reset()
        
    def _load_words(self, file_path):
        words = []
        format_spec = None
        try:
            ser_num=''
            with open(file_path, 'r') as file:
                for line in file: #this will skip first line of actual data, that is ok
                    line = line.strip()
                    if line.startswith('!!Order!!'):
                        format_spec = [field.strip().lower() for field in line.split('!!Order!!')[1].split(',') if field.strip()]
                    elif not line.startswith("#"):
                        break
                
                key = os.path.basename(file_path)
                msg_fields, policy = create_policy(format_spec, self.policies, key)
                if msg_fields and format_spec:
                    missing_fields = list(set(msg_fields) - set(format_spec))
                    format_spec += missing_fields #add missing fields
                else:
                    missing_fields = []

                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if msg_fields: # formatted (usually call history)
                        fields = line.split(',')
                        if len(fields) < len(format_spec):
                            fields.extend([''] * (len(format_spec) - len(fields)))
                        word_dict = {key: value for key, value in zip(format_spec, fields)}
                        for field in missing_fields:
                            on_missing = policy[field]["on_missing"]
                            if on_missing == 'skip':
                                continue
                            elif on_missing == 'default':
                                word_dict[field] = random.choice(policy[field]["default_value"])

                        msg_lst = [word_dict[field] for field in msg_fields]
                        if not all(msg_lst):
                            continue

                        combined_string = ' '.join(msg_lst)
                        words.append(combined_string)
                    else: # custom or spc no formatting
                        words.append(line)
                    
                    if self.generate_sernum:
                            ser_num = str(random.randint(1, 1300)) + ' '
                            if random.choice([0, 1, 2]) == 0: # in 1/3 cases
                                ser_num = ser_num.replace('1', 'a').replace('9', 'n').replace('0', 't')
                            else: # zero fill
                                while(len(ser_num)<4):
                                    ser_num = 't' + ser_num
                            self.serial_numbers.append(ser_num)
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

def create_policy(format_spec, policies, key):
    required = []
    policy = None
    has_policy = policies and key in policies.keys()
    if format_spec and has_policy: # found appropriate policy
        policy_format = [v[0] for v in sorted(policies[key].items(), key = lambda v: v[1]['position']) if v[1]['position'] >= 0]
        policy = policies[key]
        required = [v[0] for v in sorted(policy.items(), key = lambda v: v[1]['msg_position']) if int(v[1]['msg_position']) >= 0]
        if sorted(policy_format) != sorted(format_spec) and not set(required).issubset(format_spec):
            log("warning", f"{key} format not matching policy use default")
            policy = policies['exclusive']
            required = [f for f in format_spec if f not in policy.keys()]
            #required = [v[0] for v in sorted(policy.items(), key = lambda v: v[1]['msg_position']) if int(v[1]['msg_position']) >= 0]
    elif has_policy and not format_spec:
        policy = policies[key]
        required = [v[0] for v in sorted(policy.items(), key = lambda v: v[1]['msg_position']) if int(v[1]['msg_position']) >= 0]
    elif not has_policy and format_spec:
        #use default policy
        policy = policies['exclusive']
        required = [f for f in format_spec if f not in policy.keys()]
    
    return required, policy

if __name__ == '__main__':
    data_source = DataSource(file_path='data_sources/MASTER.SCP', policies_file = 'configs/message_policies.json', num_words=10)
    print('Testing super-check partial file with MASTER.SCP')
    for _ in range(5):
        print(data_source.get_next_word())
    
    data_source = DataSource(file_path='data_sources/NAQPCW.txt', policies_file = 'configs/message_policies.json', num_words=10, pre_message=True)
    print('Testing Testing call history file with NAQPCW.txt')
    for _ in range(5):
        print(data_source.get_next_word())


    data_source = DataSource(file_path='data_sources/NAQPCW.txt', policies_file = 'configs/message_policies.json', num_words=10, pre_message=True, serial=True)
    print('Testing sTesting call history file with NAQPCW.txt')
    for _ in range(5):
        print(data_source.get_next_word())


    data_source = DataSource(file_path='data_sources/CWOPS_3600-DDD.txt', policies_file = 'configs/message_policies.json', num_words=10, pre_message=True, serial=True)
    print('Testing sTesting call history file with CWOPS.txt')
    for _ in range(5):
        print(data_source.get_next_word())

    data_source = DataSource(file_path='data_sources/arrl_sweepstakes.txt', policies_file = 'configs/message_policies.json', num_words=10, pre_message=True, serial=True)
    print('Testing call history file with arrl_sweepstakes.txt')
    for _ in range(5):
        print(data_source.get_next_word())
