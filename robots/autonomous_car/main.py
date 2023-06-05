from auto import autonomous_car
from servo import Servo
from machine import I2C, Pin, Neopixel
servo=Servo(26)
servo.offset(-.2) #adjust to make it straight

i2c=I2C(sda=Pin(21), scl=Pin(22), freq=100000)
car=autonomous_car(i2c,servo)

car.drive_autonomous()

