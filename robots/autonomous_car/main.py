from auto import autonomous_car
from servo import Servo
from machine import I2C, Pin, Neopixel
import time
from lidar import Lidar
from lights import LightBar
from vl53l0x import VL53L0X
import uasyncio as asyncio


lenkservo=Servo(26)
lenkservo.set(0)
lenkservo.offset(-.2) #adjust to make it straight
lidarservo=Servo(18, min_ms=0.6 , max_ms=2.6,range_degrees=180)

i2c=I2C(sda=Pin(21), scl=Pin(22), freq=100000)
lidar=Lidar(lidarservo, VL53L0X(i2c))
kitt=LightBar()
car=autonomous_car(lidar, kitt,lenkservo, i2c)


loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt: #catch keybord interrupt
    car.m0.brake()
    car.m1.brake()
    raise            
except : #catch others
    car.m0.brake()
    car.m1.brake()
    raise   


#car.drive_autonomous()

