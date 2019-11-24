from machine import PWM

class Servo:
    def __init__(self,pin,pwm_freq=50, min_ms=1, max_ms=2, range_degrees=90):
        min_percent=100*min_ms/(1000/pwm_freq)
        max_percent=100*max_ms/(1000/pwm_freq)
        self.range_degrees=range_degrees
        self.center=(min_percent+max_percent)/2
        self.dev=(max_percent-min_percent)/2
        self.pwm = PWM(pin,freq=pwm_freq, duty=self.center)
        
    def set(self,position=None, degrees=None):
        if position is None:
            position=(degrees / self.range_degrees) * 2 - 1
        if abs(position)>1:
            raise ValueError('deviation of {} exceeds range'.format(position))
        self.pwm.duty(self.center+position*self.dev)
    
    def offset(self, position=None, degrees=None):
        if position is None:
            position=(degrees / self.range_degrees) * 2
        self.set(self.position+position)
        self.center+=self.dev*position

    
    @property
    def position(self):
        return (self.pwm.duty()-self.center)/self.dev
    
    @property
    def degrees(self):
        return (self.position+1)/2*self.range_degrees
