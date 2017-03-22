from scipy.fftpack import fft
from math import atan2

def get_circle_fft(array) :
    z = fft(array)
    N = len(z)
    #return map(lambda (i, z) : (abs(z)/N, i>N/2 and N-i or i,
    #                   int(i<=N/2 or -1), atan2(z.imag, z.real)), enumerate(z))
    #rewrite for python 3 support
    k = []
    N = len(z)
    for i in range(N) :
        r = abs(z[i]/N)
        p = atan2(z[i].imag, z[i].real)
        if i > N/2 :
            rot = -1
            omg = len(z)-i
        else :
            rot = 1
            omg = i
        k.append((r, omg, rot, p))
    return k
