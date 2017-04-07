from __future__ import print_function
from lxml import etree as ET
from copy import deepcopy

# Loaders are not well-documented. Basically we copy
# all the parts of the example xml file that contain "current"
# elements into the original tree.

def create_element(root, new_elem, plist):
    # print("CREATE_ELEMENT", plist)

    elem = root
    for p, pelem in plist:
        child = elem.find(p)
        if child is None:
            # print("NEED TO CREATE:", p, elem, pelem)
            elem.append(deepcopy(pelem))
            return
        # print("FOUND", p)
        elem = child
    # print("Updating", '/'.join([a for a,b in plist]))
    current = elem.find('current')
    if current is None:
        elem.append(deepcopy(new_elem))
    else:
        current.text = new_elem.text


def loader(xml, fname):
    root = xml.tree.getroot()
    new_tree = ET.parse(fname)
    start = new_tree.find('input')
    context = ET.iterwalk(start, events=("start", "end"))

    plist = []

    # find "current" elements in the new tree.
    # Find parent element and update the original.

    for action, element in context:
        if action == 'start':
            x = element.tag
            if element.attrib:
                x += "[@id='%s']" % element.attrib['id']
            if element.tag == 'current':
                create_element(root, element, plist)
            plist.append((x, element))
        else:
            plist.pop()


