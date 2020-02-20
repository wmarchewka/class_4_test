import pigpio
import time

pi = pigpio.pi()
print(pi.get_current_tick())