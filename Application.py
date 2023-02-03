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

def create_table(data):
    conn = sqlite3.connect(file)
    c = conn.cursor()
    table_name = 'rider_data_'+datetime.now().strftime("%Y_%m_%d")
    columns = list(data.keys())
    column_str = ', '.join(columns)
    create_table_sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                                    {column_str});"""
    print(create_table_sql)
    c.execute(create_table_sql)

def simple_DB_add(data :dict):
    conn = sqlite3.connect(file)
    c = conn.cursor()
    columns = list(data.keys())
    column_str = ', '.join(columns)
    placeholder_str = ', '.join(['?']* len(columns))
    values = list(data.values())
    table_name = 'rider_data_'+datetime.now().strftime("%Y_%m_%d")
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
        if val == None: val = 0
        val = float(val)        
        window[self.value_key].update(f'{val:.3f}')
        
analog_device_names = ['Motor voltage','Motor current','Battery voltage','Battery current','Cap Voltage']
RTD_names = ['Motor temperature','Batterry Temperature','Rider temperature','Ambient temperature']
accel_names = ['Accelerarion X', 'Accelerarion Y', 'Gyro X', 'Gyro Y', 'Gyro Z', 'Roll (bike angle)','Pitch of bike','Loop Time']
compass_names = ['Compass']


#define devices / data source
analogCard1 = Analog_Inputs()
rtdCard1 = RTD_Inputs()
AccGyro = DirectionSensors.Accelerometer()
Compass = DirectionSensors.Compass()
#Create list of IO point names

names = list(analogCard1.Poll().keys())
names += list(rtdCard1.Poll().keys())
names += list(AccGyro.Poll().keys())
names +=  list(Compass.Poll().keys())

device_labels = analog_device_names + RTD_names + accel_names + compass_names

#create a dictionary with numbered display for each name
displays = {name : LabeledNumberDisplay(key = name, label = device_label ) for name,device_label in zip(names,device_labels)}

#place each number display into a column
sensor_column = sg.Column([d.layout for d in list(displays.values())])

#main layout
layout = [[sensor_column,sg.VSeparator(),sg.Frame(title = "Graph", layout = [[sg.Graph(key = "plot", canvas_size = (200,400), graph_bottom_left = (0,0), graph_top_right= (200,400)),],
                                                                             [sg.Button("Start Recording", key = "-PlotSTARTSTOP-")]]
                                                  
                                                  ),sg.VSeparator(),sg.Frame(title = "GPS", layout = [[]])]]

#create window
window = sg.Window(title="Sensor Display", layout=layout)

#machine Definitions
class Poll_Sensors():  #call this once to start a thread
    def __init__(self, step) -> None:
        self.value = 0
        self.step = step
        self.Compass = DirectionSensors.Compass()        #self.Compass = Tag(DirectionSensors.Compass.Poll, displays['heading'] , alpha_value = .05, calibration_values = None, alarm_limits = None)
        self.AccGyro = DirectionSensors.Accelerometer()
        self.analogCard1 = Analog_Inputs()
        self.rtdCard1 = RTD_Inputs()
        self.thread = Thread(target=self.worker, daemon=True)   
        self.thread.start()
        self.RawValues = {}

    def worker(self):
        while True:
            for sensor in [self.analogCard1, self.rtdCard1, self.AccGyro, self.Compass]:
                for k,v in sensor.Poll().items():
                    #Update the display
                    self.RawValues[k] = v
            time.sleep(self.step)
   
            
class Machine():
    def __init__(self, vis) -> None:
        #tie tasks to displays once

        self.running = False
        self.vis = vis 
        self.sensors = Poll_Sensors(.5)
        time.sleep(5)
                       #	input dict location, vis locaion, filter weight or None, scaling (in1,in2,out1,out2)or None, alarm(high_high,high, low,low_low) or None 
        #analog Card
        self.Motor_Voltage = Tag(self.sensors.RawValues,'AnalogIn_0', self.vis['AnalogIn_0'], alpha_value = .05, calibration_values = (0,5,0,36), alarm_limits = (35,33,10,5) )
        self.Motor_Current = Tag(self.sensors.RawValues,'AnalogIn_1', self.vis['AnalogIn_1'], alpha_value = .05, calibration_values = (0,5,-10,10), alarm_limits = (9.9,8,-8,-9.9) ) 
        self.Battery_Voltage =Tag(self.sensors.RawValues,'AnalogIn_2', self.vis['AnalogIn_2'], alpha_value = .05, calibration_values = (0,5,0,36), alarm_limits = (35,33,10,5) )
        self.Battery_Current =Tag(self.sensors.RawValues,'AnalogIn_3', self.vis['AnalogIn_3'], alpha_value = .30, calibration_values = (0,5,-10, 10), alarm_limits = (9.9,8,-8,-9.9)) 
        self.Cap_Voltage     =Tag(self.sensors.RawValues,'AnalogIn_4', self.vis['AnalogIn_4'], alpha_value = .05, calibration_values = (0,5,0,100), alarm_limits = (95,90,10,5))    
       
        #Rtd 
        self.Motor_Temperature    = Tag(self.sensors.RawValues,'RTD_1', self.vis['RTD_1'], alpha_value = .05, calibration_values = (0,5,0,36), alarm_limits = (35,33,10,5) )
        self.Batterry_Temperature = Tag(self.sensors.RawValues,'RTD_2', self.vis['RTD_2'], alpha_value = .05, calibration_values = (0,5,0,36), alarm_limits = (35,33,10,5) )
        self.Rider_Temperature    = Tag(self.sensors.RawValues,'RTD_3', self.vis['RTD_3'], alpha_value = .05, calibration_values = (0,5,0,36), alarm_limits = (35,33,10,5) )
        self.Ambient_Temperature  = Tag(self.sensors.RawValues,'RTD_4', self.vis['RTD_4'], alpha_value = .05, calibration_values = (0,5,0,36), alarm_limits = (35,33,10,5) )
        
        #Acceleration
        self.Accelerarion_X = Tag(self.sensors.RawValues,'ACCX Angle', self.vis['ACCX Angle'], alpha_value = .05, calibration_values = (0,5,0,36))
        self.Accelerarion_Y = Tag(self.sensors.RawValues,'ACCY Angle', self.vis['ACCY Angle'], alpha_value = .05, calibration_values = (0,5,0,36))
        self.Gyro_X         = Tag(self.sensors.RawValues,'GRYX Angle', self.vis['GRYX Angle'], alpha_value = .05, calibration_values = (0,5,0,36))
        self.Gyro_Y         = Tag(self.sensors.RawValues,'GYRY Angle', self.vis['GYRY Angle'], alpha_value = .05, calibration_values = (0,5,0,36))
        self.Gyro_Z         = Tag(self.sensors.RawValues,'GYRZ Angle', self.vis['GYRZ Angle'], alpha_value = .05, calibration_values = (0,5,0,36))
        self.Roll           = Tag(self.sensors.RawValues,'CFangleX Angle', self.vis['CFangleX Angle'], alpha_value = .05, calibration_values = (0,5,0,36))
        self.Pitch          = Tag(self.sensors.RawValues,'CFangleY Angle', self.vis['CFangleY Angle'], alpha_value = .05, calibration_values = (0,5,0,36))
        self.Loop_Time      = Tag(self.sensors.RawValues,'Loop Time', self.vis['Loop Time'])
        #Compass
        self.Heading        = Tag(self.sensors.RawValues,'heading', self.vis['heading'], alpha_value = .05, calibration_values = (0,5,0,36))
        
        
    def run(self):
        if self.running:#polling opperations happening here
            

            return
        self.running = True

#Application
#create instance of Machine that polls sensors, pass refference to visual componenet
window.read(timeout = 500)
machine = Machine(displays)
time.sleep(6)
data_dict = {'Motor_Voltage':machine.Motor_Voltage.value   ,
        'Motor_Current'     :machine.Motor_Current.value   , 
        'Battery_Voltage'   :machine.Battery_Voltage.value ,
        'Battery_Current'   :machine.Battery_Current.value , 
        'Cap_Voltage'       :machine.Cap_Voltage.value     ,   
        
        'Motor_Temperature'   :machine.Motor_Temperature.value    ,
        'Batterry_Temperature':machine.Batterry_Temperature.value ,
        'Rider_Temperature'   :machine.Rider_Temperature.value    ,
        'Ambient_Temperature' :machine.Ambient_Temperature.value  ,
        
        'Accelerarion_X':machine.Accelerarion_X.value ,
        'Accelerarion_Y':machine.Accelerarion_Y.value ,
        'Gyro_X'   :machine.Gyro_X.value        ,
        'Gyro_Y'   :machine.Gyro_Y.value        ,
        'Gyro_Z'   :machine.Gyro_Z.value        ,
        'Roll'     :machine.Roll.value          ,
        'Pitch'    :machine.Pitch.value         ,
        'Loop_Time':machine.Loop_Time.value     ,
        'Heading'  :machine.Heading.value
             }

#create_table(data_dict)
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

    if recording:
        simple_DB_add(data_dict)
        
        
window.close()
