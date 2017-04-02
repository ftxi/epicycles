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


def gif(filename, size, speed, r, p, n, l, line_min=5) :
    N = len(n)
    ts = np.linspace(0, 2*np.pi, 200, endpoint=False)
    imgbase = Image.new('RGB', (2*size, 2*size), (255, 255, 255))
    drawbase = ImageDraw.Draw(imgbase)
    
    def create_image(t) :
        img = imgbase.copy()
        draw = ImageDraw.Draw(img)
        x, y = 0.0, 0.0
        _x, _y = 0.0, 0.0
        
        for k in range(N) :
            _x += r[k] * cos(l[k]*t*n[k] + p[k])
            _y += r[k] * sin(l[k]*t*n[k] + p[k])
            draw.ellipse((int(x-r[k])+size, int(y-r[k])+size, int(x+r[k])+size, int(y+r[k])+size), outline=(128, 128, 128))
            if r[k] > line_min :
                draw.line((int(x)+size, int(y)+size, int(_x)+size, int(_y)+size), fill=(0, 128, 128))
            x, y = _x, _y
        if not create_image.first:
            drawbase.line((_x+size, _y+size, create_image._x_+size, create_image._y_+size), (64, 64, 256))
        create_image.first = False
        create_image._x_, create_image._y_ = _x, _y
        return np.array(img)
    
    create_image._x_ = 0.0
    create_image._y_ = 0.0
    create_image.first = True
    images = map(create_image, np.append(ts, ts))
    imageio.mimsave(filename, images)

