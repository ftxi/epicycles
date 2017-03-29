#!usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

'''
This is a saparated package.
'''

import numpy as np
from math import sin, cos
import imageio
from PIL import Image, ImageDraw

status_bar = 0

def gif(filename, size, speed, r, p, n, l, line_min=5) :
    global status_bar
    status_bar = 0
    N = len(n)
    ts = np.linspace(0, 2*np.pi, 100)
    imgbase = Image.new('RGB', (2*size, 2*size), (255, 255, 255))
    drawbase = ImageDraw.Draw(imgbase)
    __x, __y = 0.0, 0.0
    
    def create_image(t) :
        global status_bar, __x, __y
        img = imgbase.copy()
        draw = ImageDraw.Draw(img)
        x, y = 0.0, 0.0
        _x, _y = 0.0, 0.0
        
        for k in range(N) :
            _x = r[k] * cos(l[k]*t*n[k] + p[k])
            _y = r[k] * sin(l[k]*t*n[k] + p[k])
            draw.ellipse((int(x-r[k])+size, int(y-r[k])+size, int(x+r[k])+size, int(y+r[k])+size), outline=(0, 0, 0))
            if r[k] > line_min :
                draw.line((int(x)+size, int(y)+size, int(_x)+size, int(_y)+size), fill=(0, 128, 128))
        if t!= 0:
            drawbase.line((_x, _y, __x, __y), (64, 64, 64))
        __x, __y = _x, _y
        status_bar += 1/len(ts)
        return np.array(img)
    
    images = map(create_image, ts)
    imageio.mimsave(filename, images)


'''
 N = len(self.n)
            tmp = (time.time() / N * 4 - floor(time.time() / N * 2 / pi) * 2.0 * pi) * window.SPEED
            x, y = 0.0, 0.0
            _x, _y = 0.0, 0.0
            u = 0
            for k in range(N):
                rotation = self.v[k]
                _x += self.r[k] * cos(rotation*tmp * self.n[k] + self.p[k])
                _y += self.r[k] * sin(rotation*tmp * self.n[k] + self.p[k])
                self.canvas.coords(self.epicycles_id[k], int(x - self.r[k]) + window.SIZE,\
                                   int(y - self.r[k]) + window.SIZE, int(x + self.r[k]) + window.SIZE,\
                                   int(y + self.r[k]) + window.SIZE)
                if self.r[k] > window.LINED_CIRCLE_MIN:
                    self.canvas.coords(self.through_lines_id[u], int(x) + window.SIZE,\
                                   int(y) + window.SIZE, int(_x) + window.SIZE,\
                                   int(_y) + window.SIZE)
                    u += 1
                x, y = _x, _y
                
            self.upload_tracers(int(x) + window.SIZE, int(y) + window.SIZE)
'''