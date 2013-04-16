'''
Created on Jul 6, 2012

@author: sbolduc
'''

import Tkinter
import tkMessageBox

from protocol import create_kill, encodeCrc8, encodeCrc16
from datetime import datetime

class Panel(Tkinter.Frame):
    
    def __init__(self, master, communicator, output_serializer):
        Tkinter.Frame.__init__(self, master)
        
        self.communicator = communicator
        self.output_serializer = output_serializer
        
        self.grid();
        self.grid_propagate(True);
        
        heading_label = Tkinter.Label(self)
        heading_label.grid(column=1, row=0, sticky=Tkinter.NE)
        heading_label["text"] = "Heading:"
        
        self.heading = Tkinter.StringVar()
        heading_entry = Tkinter.Entry(self, textvariable=self.heading)
        heading_entry.grid(column=2, row=0, sticky=Tkinter.N)
        heading_entry["state"] = Tkinter.DISABLED;
        
        self.heading_target = Tkinter.StringVar()
        heading_target_entry = Tkinter.Entry(self, textvariable=self.heading_target)
        heading_target_entry.grid(column=3, row=0, sticky=Tkinter.NW)
        
        depth_label = Tkinter.Label(self)
        depth_label.grid(column=1, row=1, sticky=Tkinter.E)
        depth_label["text"] = "Depth:"
        
        self.depth = Tkinter.StringVar()
        depth_entry = Tkinter.Entry(self, textvariable=self.depth)
        depth_entry.grid(column=2, row=1)
        depth_entry["state"] = Tkinter.DISABLED;
        
        self.depth_target = Tkinter.StringVar()
        depth_target_entry = Tkinter.Entry(self, textvariable=self.depth_target)
        depth_target_entry.grid(column=3, row=1, sticky=Tkinter.W)
        
        self.light = Tkinter.BooleanVar()
        light_checkbutton = Tkinter.Checkbutton(self, variable=self.light)
        light_checkbutton["text"] = "Buoy's Light:"
        light_checkbutton.grid(column=2, row=2, sticky=Tkinter.W, columnspan=2)
        light_checkbutton["state"] = Tkinter.DISABLED;
        
        self.light_target = Tkinter.BooleanVar()
        light_actuator_checkbutton = Tkinter.Checkbutton(self, variable=self.light_target)
        light_actuator_checkbutton["text"] = "Submarine's Light:"
        light_actuator_checkbutton.grid(column=3, row=2, sticky=Tkinter.W, columnspan=2)
        
        send_button = Tkinter.Button(self, command=self.sendCommand)
        send_button["text"] = "Send"
        send_button.grid(column=3, row=3, sticky=Tkinter.W)

        raw_frame = Tkinter.Frame(self)
        raw_frame.grid(column=1, row=4, columnspan=2)

        raw_scrollbar = Tkinter.Scrollbar(raw_frame)
        raw_scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        
        self.raw_text = Tkinter.Text(raw_frame, yscrollcommand=raw_scrollbar.set)
        self.raw_text["width"] = 50
        self.raw_text["height"] = 8
        self.raw_text.pack()
    
        raw_scrollbar.config(command=self.raw_text.yview)
        
        parsed_frame = Tkinter.Frame(self)
        parsed_frame.grid(column=3, row=4, columnspan=2)

        parsed_scrollbar = Tkinter.Scrollbar(parsed_frame)
        parsed_scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        
        self.parsed_text = Tkinter.Text(parsed_frame, yscrollcommand=parsed_scrollbar.set)
        self.parsed_text["width"] = 100
        self.parsed_text["height"] = 8
        self.parsed_text.pack()
        
        parsed_scrollbar.config(command=self.parsed_text.yview)
        
        self.kill_value = Tkinter.BooleanVar()
        kill_button = Tkinter.Checkbutton(self, variable=self.kill_value)
        kill_button["text"] = "Kill"
        kill_button.grid(column=4, row=0, sticky=Tkinter.NE)
        
    def appendRaw(self, data):
        line = str(datetime.now()) + ": " + self.hexStr(data) + "\n"
        self.raw_text.insert(Tkinter.END, line)
        self.raw_text.see(Tkinter.END)
        
    def hexStr(self, data):
        return ' '.join(["%02X " % ord(x) for x in data]).strip()

    def appendParsed(self, heading, depth, light):
        line = str(datetime.now()) + ": heading=" + str(heading) + ", depth=" + str(depth) + ", light=" + str(light) + "\n"
        self.parsed_text.insert(Tkinter.END, line)
        self.parsed_text.see(Tkinter.END)
        
    def setHeading(self, heading):
        self.heading.set(heading)

    def setDepth(self, depth):
        self.depth.set(depth)
        
    def setLight(self, light):
        self.light.set(light)
        
    def sendCommand(self):
        if self.validateSend():
            light = 1 if self.light_target.get() == Tkinter.ON else 0
            data = encodeCrc16(self.heading_target.get(), self.depth_target.get(), light)
            self.communicator.write(data[0])
            print "Sent heading=" + self.heading_target.get() + " depth=" + self.depth_target.get() + " light=" + str(self.light_target.get()) + " crc=" + str(data[4])
            print "Bytes: " + self.hexStr(data[0])
            self.output_serializer.write([data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]])
    
    def is_kill(self):
        return self.kill_value.get()
            
    def kill(self):
        result = tkMessageBox.askyesno(message='Are you sure you want to kill the submarine?', icon='question', title='Kill')
        if result == True:
            message = create_kill()
            self.communicator.write(message)
            print "Sent kill"
        
    def validateSend(self):
        if self.heading_target.get() == "":
            tkMessageBox.showerror("Error", "Could not send command, heading target must be set.")
            return False
        if self.depth_target.get() == "":
            tkMessageBox.showerror("Error", "Could not send command, depth target must be set.")
            return False
        try:
            heading = float(self.heading_target.get())
            if heading < 0 or heading > 359:
                tkMessageBox.showerror("Error", "Could not send command, heading target must be between 0 and 359.")
                return False
        except ValueError:
            tkMessageBox.showerror("Error", "Could not send command, heading target is not a number.")
            return False
        try:
            depth = float(self.depth_target.get())
            if depth < 0 or depth > 10:
                tkMessageBox.showerror("Error", "Could not send command, depth target must be between 0 and 10.")
                return False
        except ValueError:
            tkMessageBox.showerror("Error", "Could not send command, depth target is not a number.")
            return False
        
        return True

class Window(Tkinter.Tk):

    def __init__(self, communicator, input_serializer, output_serializer):
        Tkinter.Tk.__init__(self)
        print "Initializing main window"
        
        self.input_serializer = input_serializer
        self.output_serializer = output_serializer
        
        self.title("SONIA AUV pyng")
        self.resizable(True, True)
        self.grid_rowconfigure(1, weight=20)
        self.grid_rowconfigure(2, weight=50)
        
        self.menubar = Tkinter.Menu(self)
        
        menu = Tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Quit", command=self.close) 
        self.config(menu=self.menubar)
        
        self.panel = Panel(self, communicator, self.output_serializer)
    
    def close(self):
        self.input_serializer.close()
        self.output_serializer.close()
        self.quit()
        
    def is_kill(self):
        return self.panel.is_kill()
    
    def setHeading(self, heading):
        self.panel.setHeading(heading)

    def setDepth(self, depth):
        self.panel.setDepth(depth)
        
    def setLight(self, light):
        self.panel.setLight(light)

    def appendRaw(self, data):
        self.panel.appendRaw(data);

    def appendParsed(self, heading, depth, light):
        self.panel.appendParsed(heading, depth, light)
