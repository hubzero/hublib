from __future__ import print_function
from lxml import etree as ET
import numpy as np
import pint
from .. import ureg, Q_

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display
import shlex

from .node import Node
from .util import efind


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


class Histogram(Node):

    @staticmethod
    def format(lab):
        a = []
        for t in lab:
            try:
                num = float(t)
                a.append("{:.5g}".format(num))
            except:
                a.append(t)
        return a

    def plot(self, ax=None, horizontal=None):
        """
        Plot a rappture histogram
        """
        plt.style.use('ggplot')
        elem = self.elem

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        ci = HInfo(elem)

        xy_elem = elem.find('component/xy')
        xy = shlex.split(xy_elem.text)

        labels = Histogram.format(xy[::2])

        x_pos = np.arange(len(labels))
        y_pos = [float(x) for x in xy[1::2]]

        ax.set_title(ci.label)

        if len(labels) > 10 or horizontal is True:
            ax.barh(x_pos, y_pos, align='center')
            ax.set_yticks(x_pos)
            ax.set_yticklabels(labels)
            xlab = ci.ylab
            xunits = ci.yunits
            ylab = ci.xlab
            yunits = ci.xunits
        else:
            ax.bar(x_pos, y_pos, align='center')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(labels)
            xlab = ci.xlab
            xunits = ci.xunits
            ylab = ci.ylab
            yunits = ci.yunits

        if ci.xunits:
            xlab += " [%s]" % xunits
        ax.set_xlabel(xlab)

        if ci.yunits:
            ylab += " [%s]" % yunits
        ax.set_ylabel(ylab)
