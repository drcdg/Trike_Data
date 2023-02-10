#Application.py 
import PySimpleGUI as sg

import time
from datetime import datetime
import sqlite3

from AnalogInputs import Analog_Inputs, RTD_Inputs
import DirectionSensors

from Machine import Machine

from TagScope import line_graph, Bar_Graph

file = 'rider_data.db'
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
        
    def alarm(self, level):
        if level == 1:
            window[self.value_key].update(background_color = "yellow")
            return    
        
        elif level == 2:  
            window[self.value_key].update(background_color = "red")
            return
        
        window[self.value_key].update(background_color = "blue")

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

analog_device_names = ['Motor voltage','Motor current','Battery voltage','Battery current','Cap Voltage']
RTD_names = ['Motor temperature','Batterry Temperature','Rider temperature','Ambient temperature']
accel_names = ['Accelerarion X', 'Accelerarion Y', 'Gyro X', 'Gyro Y', 'Gyro Z', 'Roll (bike angle)','Pitch of bike','Loop Time']
compass_names = ['Compass']

device_labels = analog_device_names + RTD_names + accel_names + compass_names

#create a dictionary with numbered display for each name
displays = {name : LabeledNumberDisplay(key = name, label = device_label ) for name,device_label in zip(names,device_labels)}

machine = Machine(displays)

#place each number display into a column
sensor_column = sg.Column([d.layout for d in list(displays.values())])

power_plot = line_graph("Power",{"Motor Power": lambda :machine.Motor_Voltage.result*machine.Motor_Current.result},
                        canvass_size = (325,150), domain_range = (120, 1000))

temperature_plot = line_graph("Temperatures", {'Motor_Temperature'    :lambda: machine.Motor_Temperature.result    ,
                                                'Batterry_Temperature':lambda: machine.Batterry_Temperature.result ,
                                                'Rider_Temperature'   :lambda: machine.Rider_Temperature.result    ,
                                                'Ambient_Temperature' :lambda: machine.Ambient_Temperature.result  },
                              canvass_size = (500,150), domain_range = (120, 200))

energy_bars = Bar_Graph("Energy Bars",  graph_size=(150,150)) 

#main layout
layout = [[sensor_column,sg.VSeparator(),sg.Column(layout = [[power_plot.layout, energy_bars.layout],
                                                                             [temperature_plot.layout],
                                                                             [sg.Button("Start Recording", key = "-PlotSTARTSTOP-")]]
                                                  
                                                  )]]#,sg.VSeparator(),sg.Frame(title = "GPS", layout = [[]])

#create window
window = sg.Window(title="Sensor Display", layout=layout, finalize = True)


power_plot.start_plotting(window)
temperature_plot.start_plotting(window)
energy_bars.start_plotting(window)

#Application
#create instance of Machine that polls sensors, pass refference to visual componenet
window.read(timeout = 500)

time.sleep(6)


data_dict = {'Motor_Voltage':machine.Motor_Voltage.result   ,
        'Motor_Current'     :machine.Motor_Current.result   , 
        'Battery_Voltage'   :machine.Battery_Voltage.result ,
        'Battery_Current'   :machine.Battery_Current.result , 
        'Cap_Voltage'       :machine.Cap_Voltage.result     ,   
        
        'Motor_Temperature'   :machine.Motor_Temperature.result    ,
        'Batterry_Temperature':machine.Batterry_Temperature.result ,
        'Rider_Temperature'   :machine.Rider_Temperature.result    ,
        'Ambient_Temperature' :machine.Ambient_Temperature.result  ,
        
        'Accelerarion_X':machine.Accelerarion_X.result ,
        'Accelerarion_Y':machine.Accelerarion_Y.result ,
        'Gyro_X'   :machine.Gyro_X.result        ,
        'Gyro_Y'   :machine.Gyro_Y.result        ,
        'Gyro_Z'   :machine.Gyro_Z.result        ,
        'Roll'     :machine.Roll.result          ,
        'Pitch'    :machine.Pitch.result         ,
        'Loop_Time':machine.Loop_Time.result     ,
        'Heading'  :machine.Heading.result
             }

create_table(data_dict)
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

    power_plot.update()
    temperature_plot.update()
    energy_bars.update(labels = ['Pedal','Battery','Motor'], consumption = [0,3,22], generation = [13,5,2])
        
        
window.close()
