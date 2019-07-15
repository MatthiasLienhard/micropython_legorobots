from machine import I2C, Pin, Neopixel
import time

#examples:

#neopixel
colors={'white':0xFFFFF,
	'silver':0xC0C0C0,
	'gray':0x808080,
	'black':0x000000,
	'red':0xFF0000,
	'maroon':0x800000,
	'yellow':0xFFFF00,
	'olive':0x808000,
	'lime':0x00FF00,
	'green':0x008000,
	'aqua':0x00FFFF,
	'teal':0x008080,
	'blue':0x0000FF,
	'navy':0x000080,
	'fuchsia':0xFF00FF,
	'purple':0x800080} #html colors

np = Neopixel(Pin(27), 1) #one neopixel at pin 27
for c in colors:
    print('set neopixel 0 to {}'.format(c))
    np.set(0,colors[c])
    np.show()  
    time.sleep(.5)

#sensors
#init i2c bus
i2c = I2C(sda=Pin(21), scl=Pin(22), freq=100000)
#distance sensor
from vl53l0x import VL53L0X
dist=VL53L0X(i2c)
dist.start() #better performance (faster response, allows higher frequency)
# works up to ~1300 mm
# returns something >8000 if above.
for _ in range(100):
    print (dist.read())
    time.sleep(.1)
dist.stop() # saves power


# mpu
from mpu6050 import MPU6050
accel=MPU6050(i2c)
#print some values:
accel.val_test()
#read once:
accel_reading=accel.get_values()

#servo
#simple servo controll with PWM
#assuming servo is plugged in GPIO26 (last of the Vbat connectors)
from machine import PWM
servo = PWM(Pin(26),freq=50)
servo.duty(8) # 8% of 50 Hz = 16 milliseconds ~ about center
time.sleep(1)
for i in range(5):
    np.set(0,0xFF0000)  #red
    np.show() 
    servo.duty(13) # 26 milliseconds about max
    time.sleep(1)
    np.set(0,0x0000FF)  #blue
    np.show()  
    servo.duty(3) #6 millisec about min
    time.sleep(1)

#motors
# if pwm sound is anoying, frequency can be changed
# motors run at high speed but low torque
# for a car, it must be geared down by at least 8x
from d1motor import Motor
m0=Motor(0, i2c)
m1=Motor(1, i2c)

#maximum is about 800 ? todo:confirm
m1.speed(100)
time.sleep(1)
m1.speed(-100)
time.sleep(1)
m1.brake()

for i in range(10):
    m0.speed(i*80)
    time.sleep(.5)

for i in range(10):
    m0.speed(-i*80)
    m1.speed(800-i*80)
    time.sleep(.5)

m0.brake()
m1.brake()
