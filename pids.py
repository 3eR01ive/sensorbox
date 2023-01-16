import json

from pid import Pid


class Pids:
    def __init__(self):
        self.__pids_by_name = {}
        self.__pids_by_key = {}
        self.__create_from_config()

    def get_pids_names(self):
        return self.__pids_by_name.keys()

    def get_pid_by_name(self, name):
        return self.__pids_by_name[name]

    def has_pid_by_key(self, key):
        return key in self.__pids_by_key

    def get_pid_by_key(self, key):
        return self.__pids_by_key[key]

    def __create_from_config(self):
        with open('config/pids.json') as f:
            config = json.load(f)

            for pid_name in config.keys():
                sensor_config = config[pid_name]

                key = sensor_config['key']
                formula = sensor_config['formula']

                pid = Pid(name=pid_name, key=key, formula=formula)

                self.__pids_by_name[pid_name] = pid
                self.__pids_by_key[key] = pid
