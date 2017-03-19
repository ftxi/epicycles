from scipy.fftpack import fft
from math import atan2

def get_circle_fft(array):
    c = fft(array)
    N = len(c)
    return map(lambda (i, z) : (abs(z)/N, i>N/2 and N-i or i,
                       int(i<=N/2 or -1), atan2(z.imag, z.real)), enumerate(c))
