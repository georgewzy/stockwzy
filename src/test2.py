
import numpy as np

data = [12, 34, 29, 38, 34, 51, 29, 34, 47, 34, 55, 94, 68, 81]
x = np.arange(0,len(data))
print("x", x)
y=np.array(data)
print("y", y)
z = np.polyfit(x,y,1)
print("z", z[0])
print("{0}x + {1}".format(*z))



