import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/remeasure/'
med=cv2.imread(D+'med_end.png').astype(float)
g=cv2.GaussianBlur(med.mean(axis=2),(0,0),1.0)
gy=np.diff(g,axis=0)  # gy[y]=g[y+1]-g[y]
def scan(xs, ylo_fn, yhi_fn, sign):
    pts=[]
    for x in xs:
        y0=int(ylo_fn(x)); y1=int(yhi_fn(x))
        col=sign*gy[y0:y1,x]
        k=np.argmax(col)
        if 1<=k<len(col)-1:
            a,b,c=col[k-1],col[k],col[k+1]
            off=0.5*(a-c)/(a-2*b+c) if (a-2*b+c)!=0 else 0
        else: off=0
        pts.append((x,y0+k+0.5+off,col[k]))
    return np.array(pts)
def fit(p):
    x,y=p[:,0],p[:,1]
    A=np.vstack([x,np.ones_like(x)]).T
    m,c=np.linalg.lstsq(A,y,rcond=None)[0]
    r=y-(m*x+c)
    return m,c,r.std()
# print profile around L to understand
for x in [430,450,500,550]:
    print(x, np.round(g[440:500,x][::2]).astype(int))
