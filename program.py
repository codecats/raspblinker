import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime, timedelta
import random

GPIO.setmode(GPIO.BCM)

class Blinker:
    def __init__(self, channel, duration=5, off_duration=None, initial=True):
        if not off_duration:
            off_duration = duration
        self.duration = timedelta(0, duration)
        self.off_duration = timedelta(0, off_duration)
        self.current = datetime.now()
        self.cycle = initial
        self.channel = channel
        GPIO.setup(self.channel, GPIO.OUT, initial=self.get_state(self.cycle))

    def get_next_tick_time(self):
        if self.cycle:
            return self.current + self.duration
        return self.current + self.off_duration

    def tick(self):
        next_cycle = self.get_next_tick_time()
        now = datetime.now()
        if now > next_cycle:
            self.current = datetime.now()
            self.cycle = not self.cycle
            self.turn_on(self.cycle)

    def get_state(self, value):
        return GPIO.HIGH if not value else GPIO.LOW
    
    def turn_on(self, on=True):
        GPIO.output(self.channel, self.get_state(on))


class RandBlinker(Blinker):
    CHANGE = 30
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_after = timedelta(0, self.CHANGE)
        self.current_now = datetime.now()
        self.button_press = False

    def tick(self):
        now = datetime.now()
        if not self.current_now or now > self.current_now+self.change_after:
            self.duration = timedelta(0, random.randint(1,70)/10)
            self.off_duration = timedelta(0, random.randint(1,70)/10)
            self.current_now = now
        if self.button_press:
            self.current_now = None
            self.duration = timedelta(0, .05)
            self.off_duration = timedelta(0, .1)
        super().tick()

    def on_button_press(self, btn):
        self.button_press = True

    def on_button_release(self, btn):
        self.button_press = False
        

class PeriodicJob:
    def __init__(self, channel):
        self.channel = channel
        self.blinker = Blinker(channel, duration=.4, off_duration=.9, initial=False)
        self.is_on = False
        self.pulse = None
        self.pulse_start = None

    def tick(self):
        now = datetime.now()
        if now.minute % 15 == 0 and now.second <=10 or (self.pulse and self.pulse > now):
        #if now.second < 30:
            self.blinker.tick()
            self.is_on = True
        elif self.is_on:
            self.blinker.turn_on(False) # turn off

    def on_press(self, btn):
        if not self.pulse_start:
            self.pulse_start = datetime.now()

    def on_release(self, btn):
        if self.pulse_start:
            now =  datetime.now()
            difference = now - self.pulse_start
            self.pulse = now + difference * 4
            self.pulse_start = None



class Button:
    def __init__(self, channel):
        self.channel = channel
        GPIO.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.is_press = False
        self.is_pressed = False
        GPIO.add_event_detect(self.channel, GPIO.BOTH,callback=self.edge_detected)
        self.callback_for_press = []
        self.callback_for_release = []

    def reset(self):
        self.is_pressed = False

    def edge_detected(self, channel):
        if GPIO.input(self.channel):
            self.release()
        else:
            self.press()

    def press(self):
        self.is_pressed = False
        self.is_press = True
        for cb in self.callback_for_press:
            cb(self)

    def release(self):
        self.is_pressed = True
        self.is_press = False
        for cb in self.callback_for_release:
            cb(self)


blinker = RandBlinker(channel=4, duration=.1, off_duration=.5)
job = PeriodicJob(channel=3)
button = Button(channel=2)

button.callback_for_press = [blinker.on_button_press, job.on_press]
button.callback_for_release = [blinker.on_button_release, job.on_release]


#pin is now outputting LOW by default
try:
    while True:
        blinker.tick()
        #job.tick()
finally:
    GPIO.cleanup()
finally:
    GPIO.cleanup()

