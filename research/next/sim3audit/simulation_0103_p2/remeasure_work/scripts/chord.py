import numpy as np
def brentq(g,a,b,it=200):
    fa=g(a)
    for _ in range(it):
        m=0.5*(a+b); fm=g(m)
        if (fm>0)==(fa>0): a,fa=m,fm
        else: b=m
    return 0.5*(a+b)
def chord(f,p1,p2,D1,D2,c=(480,480)):
    r1=np.array([p1[0]-c[0],p1[1]-c[1],f],float); r1/=np.linalg.norm(r1)
    r2=np.array([p2[0]-c[0],p2[1]-c[1],f],float); r2/=np.linalg.norm(r2)
    return np.linalg.norm(D2*r2-D1*r1)
def solve_f(L,p1,p2,D1,D2,c=(480,480)):
    return brentq(lambda f: chord(f,p1,p2,D1,D2,c)-L, 200, 50000)
if __name__=='__main__':
    for ox in [-60,0,60]:
      for oy in [-60,0,40]:
        p1=(610+ox,590+oy); p2=(p1[0]-155.5,p1[1]-6.05)
        print(ox,oy, round(solve_f(4,p1,p2,90.1103,90.4360),1))
