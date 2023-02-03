from typing import Callable
import time
from threading import Thread


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
        

class Calibrate:
    def __init__(self,x1,x2,y1,y2):
        #y=mx+b 
        self.slope = (y2 - y1)/(x2 - x1)
        # b= y - mx
        self.intercept = y2 - self.slope*x2
        
    def scale(self,input_value):
        return self.slope*input_value + self.intercept
    
class Alpha_filter:
    def __init__(self, alpha = 0.05):
        self.alpha = alpha
        self.old_value = None
    
    def sample(self, new_value):
        #base case for first sample
        if not self.old_value:
            self.old_value = new_value
            return self.old_value
        
        self.old_value = (1-self.alpha) * self.old_value + self.alpha * new_value
        return self.old_value

class Alarm:
    def __init__(self, high_high, high, low, low_low, gui):
        self.high_high = high_high
        self.high = high
        self.low = low
        self.low_low = low_low
    
    def check(self,value):
        if value > self.high_high:
            #self.gui.update("high_high")
            #print("warning value very high")
            pass
        elif value > self.high:
            #self.gui.update("high")
            #print("warning value high")
            pass
        elif value < self.low_low:
            #self.gui.update("low_low")
            #print("warning value very low")
            pass
        elif value < self.low:
            #self.gui.update("low")
            #print("warning value low")
            pass
        return value
    

class Tag:
    def __init__(self,raw_Data_Dict, IO : Callable, vis, alpha_value = None, calibration_values = None, alarm_limits = None ):
        self.Data =raw_Data_Dict
        self.IO = IO
        self.vis = vis
        self.processFunctions = []
        if alpha_value:
            self.alpha_filter = Alpha_filter(alpha_value)
            self.processFunctions += [self.alpha_filter.sample]
            
        if calibration_values :
            self.calibrate = Calibrate(*calibration_values)
            self.processFunctions += [self.calibrate.scale]
        
        self.alarm = None
        if alarm_limits:
            vis = None ##
            self.alarm = Alarm(*alarm_limits, vis)
        
        self.step = .5
        self.value = 0
        self.thread = Thread(target=self.worker, daemon = True)   
        self.thread.start()

    def worker(self):
        while True:
            self.value = self.Data[self.IO]
            for p in self.processFunctions: 
               self.value = p(self.value)
            self.vis.value(self.value)
            time.sleep(self.step)
            if self.alarm: self.alarm.check(self.value)  
            
    def __repr__(self):
        return repr(self.value)
    
    def update(self):
        if self.alarm: self.alarm.check(self.value)  
        #self.vis.update(value = self)

if __name__ == "__main__":
    data = {'b':3.5}

    a = Tag(data,'b', None, alpha_value = .05, calibration_values = (0,5,100,200), alarm_limits = (190,150,120,110))
    while True:
        pass
