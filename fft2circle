from scipy.fftpack import fft
from math import *
import numpy as np


class rotCircle(object):
    def __init__(self, radius, omg, rot, p):
        self.radius = radius
        self.omg = omg
        self.rot = rot
        self.p = p
    pass


def get_circle_fft(x, y):
    z = fft(np.array(x)+1j*np.array(y))
    k = []
    N = len(z)
    for i in range(N):
        r = abs(z[i]/N)
        p = atan2(z[i].imag, z[i].real)
        if i > N/2:
            rot = -1
            omg = len(z)-i
        else:
            rot = 1
            omg = i
        k.append(rotCircle(r, omg, rot, p))
    return k

if __name__ == '__main__':
    print('use fft to get a circle list')
