def rotate(text, key):
    result = ""
    shift = key % 26

    for char in text:
        # 1. Uppercase Letters (A-Z)
        if 'A' <= char <= 'Z':
            s = ord('A')
            o = ord(char) - s
            n = (o + shift) % 26
            new_char = chr(s + n)
            result+=new_char

        # 2. Lowercase Letters (a-z)
        elif 'a' <= char <= 'z':
            s = ord('a')
            o = ord(char) - s
            n = (o + shift) % 26
            new_char = chr(s + n)
            result+=new_char

        # 3. Handle Non-alphabetic characters
        else:
            result+=char

    return result
    