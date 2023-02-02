import time
import ADS1263
import RPi.GPIO as GPIO
import librtd


class Analog_Inputs():
    def __init__(self, names = None):
        self.REF = 5.08          # Modify according to actual voltage
                    # external AVDD and AVSS(Default), or internal 2.5V

        self.ADC= ADS1263.ADS1263()
        
        if (self.ADC.ADS1263_init_ADC1('ADS1263_400SPS') == -1):
             print("Analog card connection error")
        self.ADC.ADS1263_SetMode(0) # 0 is singleChannel, 1 is diffChannel
        if names:
            self.names = names
        else:
            self.names =[f'AnalogIn_{i}' for i in range(5)]
            
            
    def Poll(self):
        channelList = [0, 1, 2, 3, 4]  # The channel must be less than 10        
        ADC_Value = self.ADC.ADS1263_GetAll(channelList)    # get ADC1 value
        values = {}
        for name in self.names:
            raw = ADC_Value[self.names.index(name)]
            if(raw >>31 ==1):
            
                values[name] = self.REF*2 - raw * self.REF / 0x80000000  
            else:
                values[name] = raw * self.REF / 0x7fffffff   # 32bit
        return values
  
  
class RTD_Inputs():
    def __init__(self, names = None):
        if names:
            self.names = names
        else:
            self.names = [f'RTD_{i}'for i in range(1,5)]
        pass
    
    def Poll(self):
        return {name: librtd.get(0,self.names.index(name)+1) for name in self.names}
  
if __name__ == "__main__":
    card = Analog_Inputs(names = ['motor voltage','motor current','motor torque','battery voltage'])
    print(*card.Poll().items())
    temps = RTD_Inputs(['Battery','Motor','Outside','Body'])
    print(*temps.Poll().items())
    
    