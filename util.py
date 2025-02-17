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

    return s

