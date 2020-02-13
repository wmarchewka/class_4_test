import os.path, pkgutil
import commander
import logger
import gpio

#pkgpath = os.path.dirname(logger.__file__)
#a =  ([name for _, name, _ in pkgutil.iter_modules([pkgpath])])
#print(a)
g = gpio.Gpio()
g.init_gpio()
g.class_property = 5
print(g.class_property)
c = commander.Commander()
print(c.codegen.gpio.class_property)
c.codegen.gpio.class_property = 8
print(g.class_property)




