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
        self.group = efind(elem, "about/group")
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

    def plot(self, single=False, ax=None, horizontal=None, stacked=False):
        """
        Plot a rappture histogram
        """
        plt.style.use('ggplot')
        elem = self.elem

        if single is False and elem.find("about/group") is not None:
            return self.mplot(ax=ax, stacked=stacked)

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        ci = HInfo(elem)

        xy = efind(elem, 'component/xy')
        if xy == "":
            xhw = efind(elem, 'component/xhw')
            xhw = shlex.split(xhw)
            labels = Histogram.format(xhw[::3])
            y_pos = [float(x) for x in xhw[1::3]]
            width = [float(x) for x in xhw[2::3]]
        else:
            xy = shlex.split(xy)
            labels = Histogram.format(xy[::2])
            y_pos = [float(x) for x in xy[1::2]]
            width = 0.7

        x_pos = np.arange(len(labels))
        ax.set_title(ci.label)

        if len(labels) > 10 or horizontal is True:
            ax.barh(x_pos, y_pos, height=width, align='center')
            ax.set_yticks(x_pos)
            ax.set_yticklabels(labels)
            xlab = ci.ylab
            xunits = ci.yunits
            ylab = ci.xlab
            yunits = ci.xunits
        else:
            ax.bar(x_pos, y_pos, width=width, align='center')
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

    def get_group_list(self, parent, gname):
        glist = []
        for child in parent:
            group = child.find("about/[group='%s']" % gname)
            if group is not None:
                glist.append(child)
        return glist

    def mplot(self, ax=None, horizontal=None, stacked=False):
        elem = self.elem

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        parent = elem.find('..')
        ci = HInfo(elem)
        glist = self.get_group_list(parent, ci.group)
        if len(glist) < 2:
            return self.plot(single=True, ax=ax, horizontal=horizontal)

        if stacked is False:
            bar_width = 0.7 / len(glist)

        for i, elem in enumerate(glist):
            label = efind(elem, "about/label")
            xy = efind(elem, 'component/xy')
            xy = shlex.split(xy)
            labels = Histogram.format(xy[::2])
            x_pos = np.arange(len(labels))
            y_pos = np.array([float(x) for x in xy[1::2]])

            if stacked:
                if i == 0:
                    prev = y_pos
                    ax.bar(x_pos, y_pos, align='center', label=label)
                else:
                    ax.bar(x_pos, y_pos, bottom=prev, align='center', label=label)
                    prev += y_pos
            else:
                ax.bar(x_pos + i*bar_width, y_pos, bar_width,  align='center', label=label)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels)
        xlab = ci.xlab
        xunits = ci.xunits
        ylab = ci.ylab
        yunits = ci.yunits

        ax.legend()
        ax.set_title(ci.desc)

        lab = ci.xlab
        if ci.xunits:
            lab += " [%s]" % ci.xunits
        ax.set_xlabel(lab)

        lab = ci.ylab
        if ci.yunits:
            lab += " [%s]" % ci.yunits
        ax.set_ylabel(lab)
