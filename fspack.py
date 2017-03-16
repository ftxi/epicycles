#!usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import division
import numpy as np
from scipy import integrate

class fourier_series :
    def __init__(self, f, N, offset=0, period=2*np.pi) :
        self.N = N
        self.period = period
        self.offset = offset
        self.c = np.zeros(2*N+1, dtype=complex)
        for n in range(-N, N+1) :
            self.c[n] = complex(integrate.quad(lambda x : (f(x)*np.exp(-2.0j*np.pi*n*x/period)).real, \
                                          offset, offset + period)[0], \
                           integrate.quad(lambda x : (f(x)*np.exp(-2.0j*np.pi*n*x/period)).imag, \
                                          offset, offset + period)[0])/period
        self._v_sn = np.vectorize(self._sn)
    
    def _sn(self, x) :
        ans = 0.0j
        for n in range(-self.N, self.N+1) :
            ans += self.c[n] * np.exp(2.0j*np.pi*n*(x-self.offset)/self.period)
        return ans
    
    def __call__(self, x) :
        return self._v_sn(x)

VAL_N = 10
FS_N = 100

if __name__ == '__main__' :
    #s = np.array([np.exp(4.0j*np.pi*x/5.) for x in range(6)])
    import matplotlib.pyplot as plt
    from scipy.interpolate import interp1d
    
    _s = np.random.rand(VAL_N) + np.random.rand(VAL_N)*1.0j
    s = np.append(_s, [_s[0]])
    
    _t = np.linspace(0., 2*np.pi, num=len(s))
    g = interp1d(_t, s)
    
    fs = fourier_series(g, FS_N)
    t = np.linspace(0., 2*np.pi, 100*VAL_N)
    
    plt.plot(fs(t).real, fs(t).imag, 'b-', label='fourier')
    plt.plot(g(t).real, g(t).imag, 'g--', label='interpolate')
    plt.plot(s.real, s.imag, 'rx', label='original')
    plt.legend()
    plt.axis([-0.4, 1.4, -0.4, 1.4])
    plt.title('Fourier Series --star')
    plt.show()
