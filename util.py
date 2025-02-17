def fmt_float(f:float):
    if f<0:
        s = fmt_float(-f)
        return f'-{s}'
    
    s = ''
    p1,p2 = f//1000,f%1000  # 1234.5
    s = f'{p2:.2f}'
    while p1>0:
        f = p1
        p1,p2 = f//1000,f%1000
        s  = f'{int(p2)},{s}'

    return strip_zero(s)
    

def strip_zero(s:str):
    p,fi,f0 = None,None,True
    for i,c in enumerate(s[::-1]):
        if c == '.':
            fi = True
            if f0:
                p = i
            break
        if c != '0' and f0:
            f0 = False
        if f0:
            p = i

    if fi is None or p is None:
        return s
    return s[:len(s)-p-1]
