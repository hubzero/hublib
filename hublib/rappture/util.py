# misc functions for rappture

def efind(elem, path):
    try:
        text = elem.find(path).text
    except:
        text = ""
    return text


def from_rap(item):
    label = item['about.label']
    if label:
        label = label.value
        
    desc = item['about.description']
    if desc:
        desc = desc.value
        
    min = item['min']
    if min:
        min = min.value
        
    max = item['max']
    if max:
        max=max.value
        
    value = item['current']
    if value:
        value = value.value
        
    units = item['units']
    if units:
        units = units.value
    
    vals = dict(
        label=label,
        desc=desc,
        min=min,
        max=max,
        value=value,
        units=units
    )
    return vals
