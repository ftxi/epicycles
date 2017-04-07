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
    line_min = options.get('line_min', 5)
    filter_zero = options.get('filter_zero', True)
    frames = options.get('frames', 400)
    fps = options.get('fps', 32)
    progresscallback = options.get('progresscallback', lambda s: print(s, file=sys.stderr))
    progresscallbackfreq = options.get('progresscallbackfreq', 5)
    
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
        writer.close()

def text(filename, r, p, n, l, **options):
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

        