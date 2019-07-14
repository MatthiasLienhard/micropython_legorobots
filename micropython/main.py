from machine import I2C, Pin, Neopixel
import robot

time.sleep_ms(500)
np = Neopixel(Pin(27), 1) 
np.set(0,0x001000)  #green
np.show()  

neopixel_pin=27
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
    np.set(0,0xFF0000)  #red
    np.show() 
    servo.duty(13)
    time.sleep(1)
    np.set(0,0x0000FF)  #blue
    np.show()  
    servo.duty(3)
    time.sleep(1)


#import robot
#auto=robot.autonomous_car(i2c, servo_pin=26)
#time.sleep_ms(500)
#auto.drive_autonomous()


np.set(0,0x010101)  #white
np.show()  
