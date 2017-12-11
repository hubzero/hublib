from __future__ import print_function
from lxml import etree as ET
from copy import deepcopy
import re
from .node import Node

class RapLoader(Node):

    @property
    def value(self):
        return self.child.text

    @value.setter
    def value(self, fname):
        RapLoader.load(self.tree, self.elem, self.child, fname)


    @staticmethod
    def copy_defaults(tree):
        # print("copy_defaults", tree)
        # Set <current> values from their <default>.  If units are required,
        # be sure to set them. Do some horrible hack to set choices.
        parse = re.compile(r"^[\s]*([0-9.]*)([\S]*)")

        for default in tree.findall(".//default"):
            par = default.find("..")
            current = par.find("current")
            if current is None:
                current = ET.SubElement(par, 'current')
                for elem in default:
                    current.append(deepcopy(elem))

        for default in tree.findall(".//default"):
            par = default.find("..")
            newtext = None
            if par.tag == 'choice':
                # now search for options
                for elem in par:
                    if elem.tag != 'option':
                        continue
                    label = elem.find('about/label').text.strip()
                    val = elem.find('value')
                    if val is not None:
                        val = val.text.strip()
                    if default.text == label or default.text == val:
                        newtext = val
                        break
            if par.tag == 'loader':
                continue
            if newtext is None:
                newtext = default.text
            current = par.find("current")
            units = par.find("units")
            if current is None:
                current = ET.SubElement(par, 'current')                
            if units is not None and units.text is not None and units.text != "":
                v, u = parse.findall(newtext)[0]
                if u == "":
                    # default did not have units set. Add them to current
                    newtext += units.text
            current.text = newtext

    @staticmethod
    def load(tree, elem, current, fname):
        # print("RapLoad", fname)
        new_tree = ET.parse(fname)
        label = new_tree.find('about/label').text
        current.text = label
        start = new_tree.find('input')
        context = ET.iterwalk(start, events=("start", "end"))

        plist = []
        root = tree.getroot()

        # find "current" elements in the new tree.
        # Find parent element and update the original.

        for action, element in context:
            if action == 'start':
                x = element.tag
                if element.attrib:
                    x += "[@id='%s']" % element.attrib['id']
                if element.tag == 'current':
                    RapLoader.create_element(root, element, plist)
                plist.append((x, element))
            else:
                plist.pop()


    # Loaders are not well-documented. Basically we copy
    # all the parts of the example xml file that contain "current"
    # elements into the original tree.

    @staticmethod
    def create_element(root, new_elem, plist):
        # print("CREATE_ELEMENT", plist)
        elem = root
        for p, pelem in plist:
            child = elem.find(p)
            if child is None:
                elem.append(deepcopy(pelem))
                return
            elem = child

        current = elem.find('current')
        if current is not None:
            elem.remove(current)
        elem.append(deepcopy(new_elem))
        RapLoader.copy_defaults(elem)

        # probably don't need this
        # current = elem.find('current')
        # v, u = parse.findall(current.text)[0]
        # if u == '':
        #     # no units. Should it have them?
        #     units = elem.find('units')
        #     if units is not None and units.text is not None and units.text != "":
        #         current.text += units.text
