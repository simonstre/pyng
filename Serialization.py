'''
Created on Jul 7, 2012

@author: sbolduc
'''

import csv

from datetime import datetime

class CsvSerializer(object):

    def __init__(self, file_name, header = []):
        self.file = open(file_name, "wb")
        self.writer = csv.writer(self.file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        header.insert(0, "timestamp")
        self.writer.writerow(header)
    
    def write(self, data = []):
        data.insert(0, str(datetime.now()))
        self.writer.writerow(data)

    def close(self):
        self.file.flush()
        self.file.close()