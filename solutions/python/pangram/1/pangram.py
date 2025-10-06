def is_pangram(sentence):
    sentence=sentence.lower()
    a=[]
    for i in range(len(sentence)):
        if sentence[i].isalpha():
            a.append(sentence[i])
    x=set(a)
    return len(x)==26
