import numpy as np
from vel import track
from geo import bp, proj
tr=track('rs'); trx=track('rx'); tro=track('ro')
def px(i):
    return np.mean([tr[i][0],trx[i][0]]), np.mean([tr[i][1],trx[i][1]])
# slope direction from stated depths only (top mid / bottom mid of board)
tm=(546.4,307.9); bm=(559.1,415.6)
T=bp(*tm,1.854); B=bp(*bm,1.701); d=(B-T)/np.linalg.norm(B-T)
print('slope dir',d,'slope len',np.linalg.norm(B-T)*100)
# ball at 0.6 s: pixel interpolated between f14 and f15 at 14.4, range 1.7288
for t06frame in [14.0,14.4,15.0]:
    a=int(np.floor(t06frame)); w=t06frame-a
    u=px(a)[0]*(1-w)+px(min(a+1,20))[0]*w; v=px(a)[1]*(1-w)+px(min(a+1,20))[1]*w
    P06=bp(u,v,1.7288)
    S={}
    for i in range(12,18):
        # find s so that proj(P06+s*d) has y == px(i)[1]
        lo,hi=-0.5,0.5
        for _ in range(80):
            m=(lo+hi)/2
            if proj(P06+m*d)[1]<px(i)[1]: lo=m
            else: hi=m
        S[i]=(lo+hi)/2
    sp={i:round((S[i+1]-S[i])*24*100,1) for i in range(12,17)}
    print('t06frame',t06frame,'speeds',sp)
