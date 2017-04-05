#!usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

'''
This is a saparated package.
'''

import numpy as np
from math import sin, cos
import imageio
from PIL import Image, ImageDraw #, ImageFilter
import time

def gif(filename, size, r, p, n, l, line_min=5, filter_zero=True, frames=200, progresscallback=lambda x, s: print(s)) :
    DIFF = 2
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
    imageio.mimsave(filename, images)

def mp4(filename, size, r, p, n, l, line_min=5, filter_zero=True, frames=400, fps=32, progresscallback=lambda s: print(s)) :
    size = 320
    DIFF = 2
    size *= DIFF
    N = len(n)
    ts = np.linspace(0, 2*np.pi, frames, endpoint=False)
    imgbase = Image.new('RGB', (2*size, 2*size), (255, 255, 255))
    drawbase = ImageDraw.Draw(imgbase)
    progress = 0
    progress_max = 2*frames
    begin = time.time()
    progresscallbackfreq = frames*2//5
    
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
    
    writer = imageio.get_writer(filename, fps=fps)
    for t in np.append(ts, ts) :
        writer.append_data(create_image(t))
        progress += 1
        if progress % progresscallbackfreq == 0 :
             eta = (time.time()-begin)/(progress/progress_max or 1)+begin-time.time()
             progresscallback('%2.2f percent finished, E. T. A. %dm %.2fs' 
                              % ((progress/progress_max*100), int(eta/60), (int(eta*100)%60)/100))
    writer.close()
    '''
    try :    
        writer = imageio.get_writer(filename, fps=fps)
        for t in np.append(ts, ts) :
            writer.append_data(create_image(t))
            progress += 1
            if progress % progresscallbackfreq == 0 :
                eta = (time.time()-begin)/(1-progress/progress_max)+begin-time.time()
                progresscallback('%2.2f percent finished, E. T. A. %dm %.2fs' 
                                 % ((progress/progress_max), int(eta/60), (int(eta*100)%60)/100))
        writer.close()
    except Exception:
        progresscallback("Oops. We've got an issue. Probably it is beacuse 'Need ffmpeg exe'"
                         " request by imageio module, which I am trying to. Wait a minute.")
        imageio.plugins.ffmpeg.download()
        progresscallback("Now, try again.")
    '''