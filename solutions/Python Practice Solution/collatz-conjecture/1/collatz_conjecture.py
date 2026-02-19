def steps(number):
    c=0
    if(number>0):
        while(number!=1):
            if (number%2==0):
                number/=2
            else:
                number=number*3+1
            c+=1
        return c
    else:
        raise ValueError("Only positive integers are allowed")