import PySimpleGUI as sg
from threading import Thread
import time
from datetime import datetime
import sqlite3

from AnalogInputs import Analog_Inputs, RTD_Inputs
import DirectionSensors

from Tags import Tag

file = 'rider_data.db';
#add timestamp
def simple_DB_add(data :dict):
    conn = sqlite3.connect(file)
    c = conn.cursor()
    columns = ['a','b','c']
    column_str = ', '.join(columns)
    placeholder_str = ', '.join(['?']* len(columns))
    values = [1,2,3]
    table_name = 'rider_data_'+datetime.now().strftime("%Y_%m_%d")
    create_table_sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                                    sample integer PRIMARY KEY,
                                    a integer,
                                    b integer NOT NULL,
                                    c integer NOT NULL);"""
    c.execute(create_table_sql)
    
    command = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholder_str})"
    c.execute(command, list(values))
    conn.commit()
    
    


class LabeledNumberDisplay():
    def __init__(self, key, label = "", init_value = 0, orientation = "r") -> None:
        self.key = key
        print(self.key)
        self.label_key = self.key + "_Label"
        self.value_key = self.key + "_Value"
        self.layout = [sg.Text(text = label, key = self.label_key),sg.Push(),sg.Text(text = init_value, key = self.value_key  )]
        if orientation  == "l":
            self.layout.reverse()

    def label(self, lbl):
        window[self.label_key].update(lbl)
    
    def value(self, val):
        window[self.value_key].update(f'{val:.3f}')
        
analog_device_names = ['Motor voltage','Motor current','Battery voltage','Battery current','Cap Voltage']
RTD_names = ['Motor temperature','Batterry Temperature','Rider temperature','Ambient temperature']
compass_names = ['Compass']
accel_names = ['Accelerarion X', 'Accelerarion Y', 'Gyro X', 'Gyro Y', 'Gyro Z', 'Roll (bike angle)','Pitch of bike']

#define devices / data source
Compass = DirectionSensors.Compass()
AccGyro = DirectionSensors.Accelerometer()
analogCard1 = Analog_Inputs(analog_device_names)
rtdCard1 = RTD_Inputs(RTD_names)

#Create list of IO point names
names = list(analogCard1.Poll().keys())
names += list(rtdCard1.Poll().keys())
compass_name = list(Compass.Poll().keys())
print(compass_name)
names += compass_name
names += list(AccGyro.Poll().keys())

#create a dictionary with numbered display for each name
displays = {name : LabeledNumberDisplay(key = name, label = name ) for name in names}

#place each number display into a column
sensor_column = sg.Column([d.layout for d in list(displays.values())])

#main layout
layout = [[sensor_column,sg.VSeparator(),sg.Frame(title = "Graph", layout = [[sg.Graph(key = "plot", canvas_size = (200,400), graph_bottom_left = (0,0), graph_top_right= (200,400)),],
                                                                             [sg.Button("Start Recording", key = "-PlotSTARTSTOP-")]]
                                                  
                                                  ),sg.VSeparator(),sg.Frame(title = "GPS", layout = [[]])]]

#create window
window = sg.Window(title="Sensor Display", layout=layout)


#machine Definitions
class task():  #call this once to start a thread
    def __init__(self,gui, step) -> None:
        self.gui = gui
        self.value = 0
        self.step = step
        self.thread = Thread(target=self.worker, daemon=True)   
        self.thread.start()

    def worker(self):
        while True:
            
            self.gui.value(self.value)
            time.sleep(self.step)
            self.value += 1


class Machine():
    def __init__(self, vis) -> None:
        #tie tasks to displays once
        self.Compass = Tag(DirectionSensors.Compass.Poll, displays['heading'] , alpha_value = .05, calibration_values = None, alarm_limits = None)
        self.AccGyro = DirectionSensors.Accelerometer()
        self.analogCard1 = Analog_Inputs(analog_device_names)
        self.rtdCard1 = RTD_Inputs(RTD_names)
        self.running = False
        self.vis = vis 
        
    
    def run(self):
        if self.running:#polling opperations happening here
            for sensor in [self.AccGyro, self.analogCard1, self.rtdCard1]:
                for k,v in sensor.Poll().items():
                    #Update the display
                    self.vis[k].value(v)
            return
        self.running = True

#Application
#create instance of Machine that polls sensors, pass refference to visual componenet
machine = Machine(displays)
simple_DB_add({})
recording = False
while True:    
    event, values = window.read(timeout = 500)
    #this is the periodic call to the machine code which only reports sensor data atm
    machine.run()

    if event == "-PlotSTARTSTOP-" and not recording:
        recording = True
        window["-PlotSTARTSTOP-"].update(text = "Stop Recording")
        print("recording started")

    elif event == "-PlotSTARTSTOP-" and recording:
        recording = False
        window["-PlotSTARTSTOP-"].update(text = "Start Recording")
        print("recording stopped")
    
    elif event == sg.WINDOW_CLOSED:
        break
    
window.close()
