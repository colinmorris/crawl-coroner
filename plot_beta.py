#!/usr/bin/env python


import sys
import scipy as sp
from scipy.special import gamma
import pylab


a = float(sys.argv[1])
b = float(sys.argv[2])


def pdf(a, b, x):
    Z = gamma(a + b) / gamma(a) / gamma(b)
    return x**(a - 1) * (1 - x)**(b - 1) / Z


x = sp.arange(0.0, 1.01, 0.01)
y = pdf(a, b, x)
ax = pylab.subplot(111)
ax.plot(x, y)

pylab.show()
