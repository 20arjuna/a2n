def preprocess(list):
    for i in range (len(list)):
        iList = list[i].split(' ')
        if(len(iList) <3):
            list.remove(list[i])
            i-=1
    return list

list =["i'm mr", "clifford", "and this is adrian", "hill and this is crash", "course", "us history"]
print(list)
print(preprocess(list))
