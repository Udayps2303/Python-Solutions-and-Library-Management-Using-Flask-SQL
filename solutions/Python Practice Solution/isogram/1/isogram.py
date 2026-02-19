def is_isogram(string):
    string=string.lower()
    if string=="":
        return True
    a=[]
    for i in range(len(string)):
        if string[i].isalpha():
            a.append(string[i])
    x=set(a)
    return len(x)==len(a)