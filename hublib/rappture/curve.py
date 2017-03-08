from __future__ import print_function
from lxml import etree as ET
import numpy as np
import pint
from .. import ureg, Q_

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display
from .node import Node
from .util import efind


class CInfo:
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


class Curve(Node):

    def plot(self, single=False, ax=None):
        elem = self.elem

        if single is False and elem.find("about/group") is not None:
            return self.mplot(ax=ax)

        """
        Plot a rappture curve
        """
        plt.style.use('ggplot')

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        ci = CInfo(elem)
        xy_elem = elem.find('component/xy')
        data = np.fromstring(xy_elem.text, sep=' \n').reshape(-1, 2)
        if ci.xscale == 'log':
            ax.set_xscale('log')
        if ci.yscale == 'log':
            ax.set_yscale('log')
        if ci.type == 'scatter':
            ax.scatter(data[:, 0], data[:, 1])
        else:
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

    def get_group_list(self, parent, gname):
        glist = []
        for child in parent:
            group = child.find("about/[group='%s']" % gname)
            if group is not None:
                glist.append(child)
        return glist

    def mplot(self, ax=None):
        plt.style.use('ggplot')
        elem = self.elem

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        parent = elem.find('..')
        ci = CInfo(elem)
        glist = self.get_group_list(parent, ci.group)
        if len(glist) < 2:
            return self.plot(single=True, ax=ax)
        for elem in glist:
            xy_elem = elem.find('component/xy')
            label = efind(elem, "about/label")
            data = np.fromstring(xy_elem.text, sep=' \n').reshape(-1, 2)
            if ci.xscale == 'log':
                ax.set_xscale('log')
            if ci.yscale == 'log':
                ax.set_yscale('log')
            if ci.type == 'scatter':
                ax.scatter(data[:, 0], data[:, 1], label=label)
            else:
                ax.plot(data[:, 0], data[:, 1], label=label)
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
