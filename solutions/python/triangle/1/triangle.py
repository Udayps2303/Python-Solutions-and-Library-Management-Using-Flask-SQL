def equilateral(sides):
    if 0 in sides:
        return False
    return sides[0]==sides[1]==sides[2]


def isosceles(sides):
    sides.sort()
    if (sides[0]+sides[1]>sides[2]):
        return sides[0]==sides[1] or sides[1]==sides[2] or sides[0]==sides[2]
    else:
        return False


def scalene(sides):
    sides.sort()
    if (sides[0]+sides[1]>sides[2]):
        return sides[0]!=sides[1]!=sides[2]
    else:
        return False