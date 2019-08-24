import json
import os
import pprint
import logging
class OpenDSSData():
    def __init__(self):
        self.config = {}
        self.data = {
            'TNet':{},
            'DNet':{},
            'TS': 0.0
        }
    
    def set_config(self, inputfile):
        filepath = os.path.abspath(inputfile)
        self.config = json.load(open(filepath))

    def print_config(self):
        pprint.pprint(self.config)
        
        
    def print_data(self):
        pprint.pprint(self.data)
        
    def log(self, text):
        logging.exception(text)

OpenDSSData = OpenDSSData()