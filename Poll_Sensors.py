import librtd

from AnalogInputs import Analog_Inputs
import DirectionSensors


x = 15*"#"
print(x)
print("Analog Hat Read")
analogCard1 = Analog_Inputs()
print (*analogCard1.Poll())
rtdCard = RTD_Inputs()
    
print(x)
print("RTD Sensor Read")
print(*rtdCard.Poll())

Compass = DirectionSensors.Compass()
AccGyro = DirectionSensors.Accelerometer()

print(x)
print("IMU Sensor Read")    
av = AccGyro.Poll()
for k,v in av.items():
    print (f"{k} : {v}")
cv = Compass.Poll()
for k,v in cv.items():
    print (f"{k} : {v}")  

