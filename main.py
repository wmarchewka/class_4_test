import os.path, pkgutil
import commander
import logger

pkgpath = os.path.dirname(logger.__file__)
a =  ([name for _, name, _ in pkgutil.iter_modules([pkgpath])])
print(a)



