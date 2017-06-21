#!usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

'''
This is a saparate package.
'''

import numpy as np
from math import sin, cos
import imageio
from PIL import Image, ImageDraw
import sys, time

FINISH_STRING = '\ndone'
DIFF = 2

def gif(filename, size, r, p, n, l, **options) :
    '''
    function epi_core.gif(filename, size, r, p, n, l, **options)
    
    Save an animated gif with given epicycle data.
    
    * filename: the output filename, usually `"*.gif"`
    * size:     output image size
    * r:        an array carrying the radius data
    * p:        phase angles, same length with `r`
    * n:        frequency data array, same length
    * l:        an array with `1` or `-1`, rotation data
    
    **options:
        - filter_zero:      whether filter the zero-frequency data in your array or not, default is `True`
        - line_min:         minimal circle radius to represent a through line(between two circle), default is `5`
        - frames:           amount of output frames, default is `200`
        - progresscallback: call this function when a part of the calculation is finished, default is to print on stderr stream
    '''
    line_min = options.get('line_min', 5)
    filter_zero = options.get('filter_zero', True)
    frames = options.get('frames', 200)
    progresscallback = options.get('progresscallback', lambda s: print(s, file=sys.stderr))
    
    size *= DIFF
    N = len(n)
    ts = np.linspace(0, 2*np.pi, frames, endpoint=False)
    imgbase = Image.new('RGB', (2*size, 2*size), (255, 255, 255))
    drawbase = ImageDraw.Draw(imgbase)
    
    def create_image(t) :
        img = imgbase.copy()
        draw = ImageDraw.Draw(img)
        x, y = 0.0, 0.0
        _x, _y = 0.0, 0.0
        
        for k in range(N) :
            if filter_zero and n[k] == 0:
                continue
            _x += r[k] * DIFF * cos(l[k]*t*n[k] + p[k])
            _y += r[k] * DIFF * sin(l[k]*t*n[k] + p[k])
            draw.ellipse((int(x-r[k]*DIFF)+size, int(y-r[k]*DIFF)+size, int(x+r[k]*DIFF)+size, int(y+r[k]*DIFF)+size), outline=(128, 128, 128))
            if r[k] > line_min :
                draw.line((int(x)+size, int(y)+size, int(_x)+size, int(_y)+size), fill=(0, 128, 128))
            x, y = _x, _y
        if not create_image.first:
            drawbase.line((_x+size, _y+size, create_image._x_+size, create_image._y_+size), (64, 64, 256))
        create_image.first = False
        create_image._x_, create_image._y_ = _x, _y
        return np.array(img.resize((size//DIFF*2, size//DIFF*2), Image.ANTIALIAS))
    
    create_image._x_ = 0.0
    create_image._y_ = 0.0
    create_image.first = True
    images = map(create_image, ts)
    progresscallback('...\ncalculation finished, saving...')
    imageio.mimsave(filename, images)
    progresscallback(FINISH_STRING)

def mp4(filename, size, r, p, n, l, **options) :
    '''
    function epi_core.mp4(filename, size, r, p, n, l, **options)
    
    Save an mp4 movie with given epicycle data.
    
    * filename: the output filename, usually `"*.mp4"`
    * size:     output image size
    * r:        an array carrying the radius data
    * p:        phase angles, same length with `r`
    * n:        frequency data array, same length
    * l:        an array with `1` or `-1`, rotation data
    
    **options:
        - filter_zero:      whether filter the zero-frequency data in your array or not, default is `True`
        - line_min:         minimal circle radius to represent a through line(between two circle), default is `5`
        - frames:           amount of output frames, default is `200`
        - progresscallback:         call this function when a part of the calculation is finished, default is to print on stderr stream
        - progresscallbackfreq:     the frequency to call a callback function, default is `50`
    '''
    line_min = options.get('line_min', 5)
    filter_zero = options.get('filter_zero', True)
    frames = options.get('frames', 400)
    fps = options.get('fps', 32)
    progresscallback = options.get('progresscallback', lambda s: print(s, file=sys.stderr))
    progresscallbackfreq = options.get('progresscallbackfreq', 50)
    
    size *= DIFF
    N = len(n)
    ts = np.linspace(0, 2*np.pi, frames, endpoint=False)
    imgbase = Image.new('RGB', (2*size, 2*size), (255, 255, 255))
    drawbase = ImageDraw.Draw(imgbase)
    progress = 0
    progress_max = 2*frames
    begin = time.time()
    
    def create_image(t) :
        img = imgbase.copy()
        draw = ImageDraw.Draw(img)
        x, y = 0.0, 0.0
        _x, _y = 0.0, 0.0
        
        for k in range(N) :
            if filter_zero and n[k] == 0:
                continue
            _x += r[k] * DIFF * cos(l[k]*t*n[k] + p[k])
            _y += r[k] * DIFF * sin(l[k]*t*n[k] + p[k])
            draw.ellipse((int(x-r[k]*DIFF)+size, int(y-r[k]*DIFF)+size, int(x+r[k]*DIFF)+size, int(y+r[k]*DIFF)+size), outline=(128, 128, 128))
            if r[k] > line_min :
                draw.line((int(x)+size, int(y)+size, int(_x)+size, int(_y)+size), fill=(0, 128, 128))
            x, y = _x, _y
        if not create_image.first:
            drawbase.line((_x+size, _y+size, create_image._x_+size, create_image._y_+size), (64, 64, 256))
        create_image.first = False
        create_image._x_, create_image._y_ = _x, _y
        return np.array(img.resize((size//DIFF*2, size//DIFF*2), Image.ANTIALIAS))
    
    create_image._x_ = 0.0
    create_image._y_ = 0.0
    create_image.first = True
    
    try :
        writer = imageio.get_writer(filename, fps=fps)
        for t in np.append(ts, ts) :
            writer.append_data(create_image(t))
            progress += 1
            if progress % progresscallbackfreq == 0 :
                 eta = (time.time()-begin)*(progress_max - progress)/progress
                 progresscallback('-+-\n%2.2f percent finished, E. T. A. %dm %ds' 
                                  % ((progress/progress_max*100), eta//60, int(eta)%60))
        progresscallback('...\ncalculation finished, saving...')
        writer.close()
        progresscallback(FINISH_STRING)
    except imageio.core.NeedDownloadError :
        progresscallback("Oops. It is said that 'Need ffmpeg exe' by imageio module, \n"
                         "which I am trying to. Wait a minute.")
        imageio.plugins.ffmpeg.download()
        progresscallback("\nNow, try again.")
    except KeyboardInterrupt :
        pass      #force stop the progress
    finally :
        writer.close()

def text(filename, r, p, n, l, **options) :
    filter_zero = options.get('filter_zero', True)
    str_x = '%2.2f*cos(%d*t%s)'
    str_y = '%2.2f*sin(%d*t%s)'
    sx = ''
    sy = ''
    def sign_(x) :
        if x >= 0 :
            return '+%2.2f' % x
        else :
            return '%2.2f' % x
    with open(filename, 'w') as file_ :
        N = len(n)
        for k in range(N) :
            if filter_zero and n[k] == 0:
                continue
            sx += '+' + str_x % (r[k], n[k]*l[k], sign_(p[k]))
            sy += '+' + str_y % (r[k], -n[k]*l[k], sign_(-p[k]))
        file_.write('x(t) = ' + sx[1:] + '\n')
        file_.write('y(t) = ' + sy[1:] + '\n')

def init(points, **options) :
    '''
    init(points, **options)
    
    experimental
    * points is an array of complex numbers, e.g. [x1+1.0j*y1, x2+1.0j*y2, ...]
    
    **options:
        - interpolation: interpolation algorithm, default is none.
            possible value are `'none'`, `'linear'` and `spline`
        - data:          the amount of interpolate points, default is 1024
        - sort_:         whether sort the circle by radius or not, default is `False`
        - min_:          minimum circle size, default is 0.25
        
    '''
    from scipy.interpolate import interp1d, splprep, splev
    import fft2circle
    interpolation = options.get('interpolation', 'none')
    data = options.get('data', 1024)
    sort_ = options.get('sort_', False)
    min_ = options.get('min_', 0.25)
    if interpolation == 'none' :
        array = points
    elif interpolation == 'linear' :
        _z = np.append(points, [points[0]])
        _t = np.arange(len(_z))
        f = interp1d(_t, _z)
        t = np.linspace(0, len(_z)-1, data)
        array = f(t)
    elif interpolation == 'spline' :
        _z = np.append(points, [points[0]])
        tck, u = splprep([_z.real, _z.imag], s=0)
        unew = np.linspace(0, 1, data)
        out = splev(unew, tck)
        array = out[0] + out[1]*1.0j
    acircle = fft2circle.get_circle_fft(array)
    if sort_ :
        acircle = sorted(acircle, key=lambda _: -_[0])
    r = []
    n = []
    l = []
    p = []
    for r_, n_, l_, p_ in acircle:
        if r_ >= min_ :
            r.append(r_)
            n.append(n_)
            l.append(l_)
            p.append(p_)
    return np.array(r), np.array(p), np.array(n), np.array(l)

if __name__ == '__main__' :
    '''
    A sample code.
    '''
    size = 80
    array = np.array([np.exp(x*4.0j*np.pi/5) for x in range(5)]) * size
    data = init(array, interpolation='linear', sort_=True, min_=10)
    gif('star.gif', size, *data)

    
