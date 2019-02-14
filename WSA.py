import operator
# text is a list of words
def createDictionary (text, keywords):
    my_dict = {}
    for (i in range len(text)):
        my_dict.update({keywords[i], text.index(keywords)})
    return my_dict

def sortByIndex(dict):
    sorted_dict = sorted(dict.items(), key=operator.itemgetter(1))
    return sorted_dict
