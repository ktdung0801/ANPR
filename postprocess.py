"""
def post_long(s):
    # remove duplicate
    s = list(s)
    for i in range(len(s) - 1):
        if s[i] == '0' and s[i + 1] == '0':
            s[i + 1] = ''
        if s[i] == 'D' and s[i + 1] == 'D':
            s[i + 1] = ''
    for i in range(len(s)):
        if i != 2 and s[i] == 'B':
            s[i] = '8'
    s = "".join(s)
    return s



def post_square(s):
    s = list(s)
    for i in range(len(s)):
        if i == 2 and s[i] == '8':
            s[i] = 'B'
        if i == 2 and s[i] == '0':
            s[i] = 'D'
        if i == 2 and s[i] == '5':
            s[i] = 'S'
    s = "".join(s)
    return s
"""