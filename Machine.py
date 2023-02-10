from threading import Thread
import time

from AnalogInputs import Analog_Inputs, RTD_Inputs
import DirectionSensors


from Tags import Tag

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
        self.Motor_Temperature    = Tag(self.sensors.RawValues,'RTD_1', self.vis['RTD_1'], alpha_value = .05, calibration_values = (0,5,0,25), alarm_limits = (35,33,10,5) )
        self.Batterry_Temperature = Tag(self.sensors.RawValues,'RTD_2', self.vis['RTD_2'], alpha_value = .05, calibration_values = (0,5,0,25), alarm_limits = (35,33,10,5) )
        self.Rider_Temperature    = Tag(self.sensors.RawValues,'RTD_3', self.vis['RTD_3'], alpha_value = .05, calibration_values = (0,5,0,25), alarm_limits = (35,33,10,5) )
        self.Ambient_Temperature  = Tag(self.sensors.RawValues,'RTD_4', self.vis['RTD_4'], alpha_value = .05, calibration_values = (0,5,0,25), alarm_limits = (35,33,10,5) )
        
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
        
        self.updating_view_tags = [self.Motor_Voltage,
                        self.Motor_Current  , 
                        self.Battery_Voltage,
                        self.Battery_Current , 
                        self.Cap_Voltage     ,   
        
                        self.Motor_Temperature    ,
                        self.Batterry_Temperature ,
                        self.Rider_Temperature    ,
                        self.Ambient_Temperature  ,
        
                        self.Accelerarion_X ,
                        self.Accelerarion_Y ,
                        self.Gyro_X        ,
                        self.Gyro_Y        ,
                        self.Gyro_Z        ,
                        self.Roll         ,
                        self.Pitch,
                        self.Loop_Time,
                        self.Heading
                             ]
      

    def run(self):
        if self.running:#polling opperations happening here
            
            for tag in self.updating_view_tags:
                tag.update()
        
            return
        self.running = True
