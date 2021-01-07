
def evaluate_scinum(scinum):
    floatnum = float(scinum[:scinum.find('e')])
    expo = int(scinum[scinum.find('e')+1:])
    return floatnum * (10 ** expo)