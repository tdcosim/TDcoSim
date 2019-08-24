import json
import os
import logging
import pprint
class GlobalData():
    def set_config(self, inputfile):
        filepath = os.path.abspath(inputfile)
        self.config = json.load(open(filepath))

    def set_TDdata(self):
        self.data = {
            'TNet':{},
            'DNet':{},
            'TS': 0.0
        }                   

    def print_config(self):
        pprint.pprint(self.config)
                
    def print_data(self):
        pprint.pprint(self.data)
        
    def log(self, text):
        logging.exception(text)

GlobalData = GlobalData()