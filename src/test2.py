
import numpy as np

red_az = [12,12]
x = np.arange(0, len(red_az))
y = np.array(red_az)
print("xx", x, y, type(x), type(y))
z = np.polyfit(x, y, 1)
print("z",z)
