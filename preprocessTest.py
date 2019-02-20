def preprocess(list):
    for i in range (len(list)-1, -1, -1):
        iList = list[i].split(' ')
        if(len(iList) <3):
            list.remove(list[i])
    return list

list =["i'm mr", "clifford", "and this is adrian", "hill and this is crash", "course", "us history"]
print(list)
print(preprocess(list))
