def is_valid(isbn):
    a=[]
    isbn=isbn.replace("-","")
    if len(isbn)!=10:
        return False
    if not (isbn[:9].isdigit() and (isbn[9].isdigit() or isbn[9] == 'X')):
        return False
    for i in range(len(isbn)):
        if isbn[i] == 'X':
            a.append(10)
        else:
            a.append(int(isbn[i]))
    c=0
    for i in range(len(a)):
        c+=a[i]*(10-i)
    return c%11==0
        