from machine import I2C, Pin, Neopixel
import robot

time.sleep_ms(500)
#np = Neopixel(Pin(5), 4) 
np.set(0,0x001000)  #green


neopixel_pin=5
pinsVbatt=[26,33,14,5,13]
pins3v=[4,12,2,15,0]
neopixel_pin=27
uart_pins=[16,17] #first 4 pin connecter

i2c_pins=[21,22] #2nd and 3rd 4 pin connector
i2c = I2C(sda=Pin(21), scl=Pin(22), freq=100000)
i2c.scan()
# i2c adressen:
#48 (=0x30): motor driver (im gehaeuse)
#104 (=0x68): MPU 6050 (accel/gyro/temp)
#41 (=0x29): vl53l0x

np.set(0,0x0000FF)  #blue?

from machine import PWM
servo = PWM(Pin(26),freq=50)
servo.duty(8)
time.sleep(1)

for i in range(5):
    for pos in list(range(101))+(list(range(99,0,-1))):
        #set neopixel
        for i in range(1,5):
            c=int(max(0,255-10*abs(i*20-pos))* 0x0010000)
            np.set(i,c, update=False)
        np.show()         
        #set servo
        servo.duty(pos/25+5)
        time.sleep_ms(10)

servo.duty(7)
#import robot
#auto=robot.autonomous_car(i2c, servo_pin=26)
#time.sleep_ms(500)
#auto.drive_autonomous()


np.set(1,0x010101, num=4 )  #white
from d1motor import Motor
m0=Motor(0, i2c)
m1=Motor(1, i2c)

#maximum is about 800 ? todo:confirm
m1.speed(50)
m0.speed(50)
time.sleep(.5)
m1.speed(-50)
m0.speed(-50)
time.sleep(.5)
m1.brake()
m0.brake()