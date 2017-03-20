from scipy.fftpack import fft
from math import atan2

def get_circle_fft(array):
    c = fft(array)
    N = len(c)
    return map(lambda (i, z) : (abs(z)/N, i>N/2 and N-i or i,
                       int(i<=N/2 or -1), atan2(z.imag, z.real)), enumerate(c))
#this can not run in python3.6 and I can not debug so I use another def which has the same input and output
def get_circle_fft2(arr):
    z = fft(arr)
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
        k.append([r, omg, rot, p])
    return k
