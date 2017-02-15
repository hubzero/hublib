from __future__ import print_function
from lxml import etree as ET
import numpy as np
import pint
from .. import ureg, Q_

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display


def efind(elem, path):
    try:
        text = elem.find(path).text
    except:
        text = ""
    return text


class HInfo:
    def __init__(self, elem):
        self.label = efind(elem, "about/label")
        self.desc = efind(elem, "about/description")
        self.xlab = efind(elem, "xaxis/label")
        self.xdesc = efind(elem, "xaxis/description")
        self.xunits = efind(elem, "xaxis/units")
        self.xscale = efind(elem, "xaxis/scale")
        self.ylab = efind(elem, "yaxis/label")
        self.ydesc = efind(elem, "yaxis/description")
        self.yunits = efind(elem, "yaxis/units")
        self.yscale = efind(elem, "yaxis/scale")
        self.style = efind(elem, "about/style")
        self.type = efind(elem, "about/type")


def hist_plot(elem, ax=None):
    """
    Plot a rappture histogram
    """
    plt.style.use('ggplot')

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    ci = CInfo(elem)
    xy_elem = elem.find('component/xy')
    data = np.fromstring(xy_elem.text, sep=' \n').reshape(-1, 2)

    ax.plot(data[:, 0], data[:, 1])

    ax.set_title(ci.label)

    lab = ci.xlab
    if ci.xunits:
        lab += " [%s]" % ci.xunits
    ax.set_xlabel(lab)

    lab = ci.ylab
    if ci.yunits:
        lab += " [%s]" % ci.yunits
    ax.set_ylabel(lab)


