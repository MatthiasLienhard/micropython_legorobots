import d1motor
import time
import machine
from math import copysign
from machine import I2C, Pin, PWM
#from esp32_vl53l0x import VL53L0X   
from vl53l0x import VL53L0X   
import random
#i2c = I2C(-1,Pin(22), Pin(21), freq=100000)



class autonomous_car:
    def __init__(self, i2c,servo_pin,  min_speed=100, max_speed=500):
        self.m0= d1motor.Motor(0, i2c)
        self.m0.frequency(1000) # 10khz -> quiet
        self.dist_sensor=VL53L0X(i2c)
        self.dist_sensor.start()
        self.dist=self.dist_sensor.read()
        #self.pause_pin=Pin(pause_pin, machine.Pin.IN, machine.Pin.PULL_UP) #its pulled low by a cable in operating mode
        #esp32.wake_on_ext0(pin = self.pause_pin, level = esp32.WAKEUP_ALL_LOW)
        #does not work because of exposed pins
        self.servo = PWM(Pin(servo_pin),freq=50)
        # duty for servo is between 26 - 122 (~180 degrees)
        self.servo.duty(79) # about center
        self.direction=0
        self.current_speed=0
        self.actual_speed=0
        self.steer()
        self.min_speed=min_speed
        self.max_speed=max_speed
        

    def steer(self):
        if abs(self.direction)>1:
            raise ValueError('direction should be between -1 and 1')
        dc=round(self.direction*15+79)
        self.servo.duty(dc)

    def drive(self, speed=None):
        if speed is None:
            speed=self.current_speed
        if abs(speed) > 0:
            mspeed=round(self.min_speed+abs(speed)*(self.max_speed-self.min_speed)/100)            
            self.m0.speed(int(copysign(mspeed, speed)))
        else:    
            self.m0.sleep()

    def print_status(self, msg):
        print('{}d={}, motor speed={}%,direction={},  real speed={}'.format(
            msg,
            self.dist,
            round(self.current_speed),
            round(self.direction*10), 
            round(self.actual_speed,2)))

    def drive_autonomous(self, accel=10):
        now=prev=time.ticks_ms()
        d_prev=self.dist
        target_speed=0
        cycle_count=0
        while True:
            try:
                now=time.ticks_ms()  
                if(now-prev>100):              
                    try:            
                        self.dist=self.dist_sensor.read()#sometimes the reading fails
                    except:
                        print('dist sensor error')
                        d=d_prev
                    #calculate actual speed
                    self.actual_speed=(d_prev-self.dist)/(now-prev)     #(mm/ms==m/s)   
                    d_prev=self.dist
                    prev=now

                if self.dist>1000:
                    self.dist=1000                
                if self.dist<300:            
                    #turn around
                    #self.direction=random.randrange(-1,2,2)
                    self.m0.brake() 
                    self.direction=1
                    self.current_speed=-20
                    self.print_status('<- ')
                    self.steer()
                    self.drive()         
                    time.sleep(1)
                    self.direction*=-1
                    self.current_speed=20
                    self.steer()
                    self.drive()
                    time.sleep(1)
                    self.direction=0
                else:
                    self.direction+=random.randrange(-10,11)/100
                    if abs(self.direction)>1:
                        self.direction=copysign(1,self.direction)
                    self.steer()
                    target_speed=self.dist/10-20
                    if target_speed>self.current_speed:
                        self.current_speed+=copysign(accel,target_speed-self.current_speed) #beware overshooting
                    else:
                        self.current_speed=target_speed
                    #if cycle_count % 10 ==0:
                    self.print_status('-> ')        
                    self.drive()

                time.sleep(.1)#update 10/second
                cycle_count+=1
            except: #catch keybord interrupt and others
                self.m0.brake()
                raise            
        self.m0.brake() 
        
