Epicycles
============

A small program to display epicycles with given image.

Introduction: <https://sclereid.github.io/epicycles>

Wikipedia page about *deferent and epicycle*: <https://en.wikipedia.org/wiki/Deferent_and_epicycle>

Inspired by this article: [*The Mathematical Power of Epicyclical Astronomy*](http://www.u.arizona.edu/%7Eaversa/scholastic/Mathematical%20Power%20of%20Epicyclical%20Astronomy%20%28Hanson%29.pdf)

> In the Hipparchian and Ptolemaic systems of astronomy, the epicycle (from Ancient Greek: ἐπίκυκλος, literally on the circle, meaning circle moving on another circle) was a geometric model used to explain the variations in speed and direction of the apparent motion of the Moon, Sun, and planets. In particular it explained the apparent retrograde motion of the five planets known at the time. Secondarily, it also explained changes in the apparent distances of the planets from Earth.

![snapshot](resource/snapshot.png)



### Status:

***Improving***

More Features:
------------

**better interaction with users:**

* [x] allow using a background picture
* [x] more user defined variables
* [ ] colorful background
* [x] better tracers
* [x] export as animated gif (as well as mp4)

**create delicate epicycles:**

* [ ] <s>use fourier series instead of discrete fourier transform</s>
* [x] use both clockwise and counterclockwise rotations (suggested by [zzytyy](https://github.com/zzyztyy))

**documentation:**
* [x] write some doc about its principles

Note:
-----------

This is a GPL Licensed version. See [LICENSE.md](LICENSE.md) for more information.

### Usage:

If you were running from the source, remember to install [python](https://www.python.org), [numpy](http://www.numpy.org) and [scipy](http://www.scipy.org) in advance. Python Imaging Library (aka. [PIL](http://www.pythonware.com/products/pil/)) and [imageio](http://imageio.github.io) is also required for image processing, however, they are not necessary for computation. 

Download from the releases or run the source file in python. Should be simple enough.

***REMARK***

Due to the frequent Mac OS update, the previous release has some minor issues (the label on the buttons are now invisible). However, thanks to the same reason, I didn't made it to rebuilt a satisfying program. So, for those who just want to have a try, plese use the latest release. After drawing the image, press the fifth and the sixth button sequentially. Or, if you are familiar with command lines, a better solution is to run the following lines. (April 2019)

```
pip install numpy scipy imageio
python epicycle.py
```

Have fun!
