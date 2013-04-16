'''
Created on Jul 6, 2012

@author: sbolduc
'''

from itertools import permutations
from serial import Serial, SerialException
from time import sleep
from threading import Thread
from Tkinter import ON, OFF

from protocol import create_kill, decodeCrc8, decodeCrc16

class SerialCommunicator(object):

    def __init__(self):
        print "Initializing communicator"
            
    def connect(self, baudrate=9600):
        port_ids = self.scan()
        
        if len(port_ids) > 0:
            port_id = port_ids[0]
            self.connect_to_port_id(port_id, baudrate)
        else:
            print "Could not find serial port"
            
    def connect_to_port(self, device, baudrate=9600):
        self.socket = Serial()
        self.socket.port = device
        self.socket.setBaudrate(baudrate);
        self.socket.open()
        print "Connected on " + self.socket.portstr
        
    def connect_to_port_id(self, port_id=0, baudrate=9600):
        self.socket = Serial(port_id)
        self.socket.setBaudrate(baudrate);
        print "Connected on " + self.socket.portstr
        
    def read(self, size=4):
        return self.socket.read(size)
    
    def scan(self):
        port_ids = []
        for i in range(4):
            try:
                port = Serial(i)
                port_ids.append(i)
                port.close()
            except SerialException:
                pass
        return port_ids
    
    def write(self, data):
        self.socket.write(data)
    
    def kill_submarine(self):
        self.socket.write(create_kill())

class AcquisitionLoop(Thread):

    def __init__(self, communicator, window, serializer):
        Thread.__init__(self) 
        
        self.data = []
        
        self.communicator = communicator
        self.window = window
        self.serializer = serializer
        
        self.setDaemon(True)

    def run(self):
        while(1):
            data = self.communicator.read(1)
            
            self.data.append(data)
            
            if len(self.data) == 4:
                self.window.appendRaw(self.data)
                
                strData = ""
                for i in range(4):
                    strData += self.data[i]
                    
                decoded_data = decodeCrc16(strData)
                
                # Good CRC
                if decoded_data[4] == decoded_data[5]:
                    
                    print "Good CRC"
                    
                    for i in range(4):
                        self.data.pop(0)
                        
                    heading = decoded_data[1]
                    depth = decoded_data[2]
                    light = decoded_data[3]
                    crc = decoded_data[4]
                    calculated_crc = decoded_data[5]
                    first_byte = decoded_data[6]
                    second_byte = decoded_data[7]
                    first_crc = decoded_data[8]
                    second_crc = decoded_data[9]
                
                    self.window.appendParsed(heading, depth, light)
                    self.window.setHeading(heading)
                    self.window.setDepth(depth)
                    self.window.setLight(ON if light == 1 else OFF)
                        
                    self.serializer.write([heading, depth, light, crc, calculated_crc, first_byte, second_byte, first_crc, second_crc])
                else:
                    permutated_data = None
                    #permutated_data = self.check_permutations(self.data)
                    if permutated_data != None:
                        print "A permutation was good!"
                        
                        heading = decoded_data[1]
                        depth = decoded_data[2]
                        light = decoded_data[3]
                        crc = decoded_data[4]
                        calculated_crc = decoded_data[5]
                        first_byte = decoded_data[6]
                        second_byte = decoded_data[7]
                        first_crc = decoded_data[8]
                        second_crc = decoded_data[9]
                    
                        self.window.appendParsed(heading, depth, light)
                        self.window.setHeading(heading)
                        self.window.setDepth(depth)
                        self.window.setLight(ON if light == 1 else OFF)
                            
                        self.serializer.write([heading, depth, light, crc, calculated_crc, first_byte, second_byte, first_crc, second_crc])
                    else:
                        discarded_data = self.data.pop(0)
                        print "Did not found permutation, discarded " + discarded_data
        print "Exited acquisition loop"

    def check_permutations(self, data):
        for p in list(permutations(data)):
            strData = ""
            for i in range(4):
                strData += p[i]
                            
            decoded_data = decodeCrc16(strData)
            if decoded_data[4] == decoded_data[5]:
                return decoded_data
        return None

class KillLoop(Thread):

    def __init__(self, communicator, window):
        Thread.__init__(self)
        
        self.communicator = communicator
        self.window = window
        
        self.setDaemon(True)

    def run(self):
        while(1):
            if self.window.is_kill() == True:
                self.communicator.kill_submarine()
                
                print "Sent kill command!"
            
            sleep(1)
                
