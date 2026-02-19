def is_armstrong_number(number):
    x=number
    c=0
    s=0
    y=len(str(number))
    while(number>0):
        c=number%10
        number=number//10
        s=s+c**y
    if(s==x):
        return True
    else:
        return False