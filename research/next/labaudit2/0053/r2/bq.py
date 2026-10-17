def brentq(g,a,b,tol=1e-9):
    fa=g(a); fb=g(b)
    assert fa*fb<0,(fa,fb)
    for _ in range(200):
        m=(a+b)/2; fm=g(m)
        if fa*fm<=0: b,fb=m,fm
        else: a,fa=m,fm
        if b-a<tol: break
    return (a+b)/2
