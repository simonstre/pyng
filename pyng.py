'''
Created on Jul 5, 2012

@author: sbolduc
'''

import communication
import gui
import serialization

import sys

from datetime import datetime

class Pyng(object):
    
    def __init__(self):
        print "Starting Pymodem"
        self.input_serializer = serialization.CsvSerializer(str(datetime.now()) + "-input.csv", ["heading", "depth", "light", "crc", "calculated_crc", "first_byte", "seconde_byte", "first_crc", "second_crc"])
        self.output_serializer = serialization.CsvSerializer(str(datetime.now()) + "-output.csv", ["heading", "depth", "light", "crc", "first_byte", "seconde_byte", "first_crc", "second_crc"])
        self.communicator = communication.SerialCommunicator()
        self.window = gui.Window(self.communicator, self.input_serializer, self.output_serializer)
        self.acquisition_loop = communication.AcquisitionLoop(self.communicator, self.window, self.input_serializer)
        self.kill_loop = communication.KillLoop(self.communicator, self.window)
    
    def start(self, device):
        if (device): 
            self.communicator.connect_to_port(device, 9600)
            self.acquisition_loop.start()
            self.kill_loop.start()
        self.window.mainloop()
        self.window.destroy()
        
if __name__ == '__main__':

    device = sys.argv[1] if len(sys.argv) > 1 else ""

    pyng = Pyng()
    pyng.start(device)
