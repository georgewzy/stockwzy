import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
x = np.linspace(0, 2 * np.pi, 500)
y = np.sin(x) * np.exp(-x)
fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212, sharex= ax1)
ax1.plot(x, y)
ax1.set_title("折线图")

ax2.scatter(x, y)

plt.suptitle("一张画布两个子图,并共享y坐标")
# 删除空隙wspace为两图的水平距离，hspace为两图的垂直距离
fig.subplots_adjust(wspace=0.1, hspace=0)
plt.show()