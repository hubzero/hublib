# misc functions for rappture


def efind(elem, path):
    try:
        text = elem.find(path).text
    except:
        text = ""
    return text
