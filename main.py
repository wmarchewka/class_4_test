import os.path, pkgutil
import commander
import logger
import gpio

#pkgpath = os.path.dirname(logger.__file__)
#a =  ([name for _, name, _ in pkgutil.iter_modules([pkgpath])])
#print(a)
g = gpio.Gpio().init_gpio()
c= commander.Commander()
print(c.rotary)




