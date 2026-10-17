import cv2, numpy as np
med=cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit2/0037/m2/median_x.png')
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY).astype(float)
m=g>30
def topb(xs):
    pts=[]
    for x in xs:
        col=m[300:700,x]
        idx=np.where(col)[0]
        if len(idx)==0: continue
        # subpixel: use gray profile crossing 30-> find first idx
        y=idx[0]+300
        # subpixel via linear interp of gray around threshold mid (bg~0, table~?)
        prof=g[y-3:y+4,x]
        lo,hi=prof[0],prof[-1]
        half=(lo+hi)/2
        k=np.where(prof>=half)[0][0]
        if k>0:
            yy=y-3+k-1+(half-prof[k-1])/(prof[k]-prof[k-1]+1e-9)
        else: yy=y-3
        pts.append((x,yy))
    return np.array(pts)
def fitline(p):
    A=np.c_[p[:,0],np.ones(len(p))]
    a,b=np.linalg.lstsq(A,p[:,1],rcond=None)[0]
    r=p[:,1]-(a*p[:,0]+b)
    # robust refit
    k=np.abs(r)<2.5*np.std(r)+0.3
    a,b=np.linalg.lstsq(A[k],p[k,1],rcond=None)[0]
    r=p[k,1]-(a*p[k,0]+b)
    return a,b,np.std(r),k.sum()
L=topb(range(225,425)); B1=topb(list(range(600,650))+list(range(830,900))); R=topb(range(935,1125))
for n,p in [('left',L),('back',B1),('right',R)]:
    print(n,fitline(p))
# front edge of top surface: strongest negative vertical gradient below top surface (top bright -> face dark)
gy=cv2.Sobel(cv2.GaussianBlur(g,(3,3),0),cv2.CV_64F,0,1,ksize=3)
F=[]
for x in range(240,1110,2):
    y0=int(537+(x-211)*(588-537)/(1138-211))
    seg=-gy[y0-8:y0+9,x]
    k=np.argmax(seg)
    if 0<k<len(seg)-1:
        d=(seg[k-1]-seg[k+1])/(2*(seg[k-1]-2*seg[k]+seg[k+1]))
    else: d=0
    F.append((x,y0-8+k+d))
F=np.array(F)
print('front',fitline(F))
np.save('/home/user/quantiphy-challenge/research/next/labaudit2/0037/m2/edges.npy',{'L':L,'B':B1,'R':R,'F':F},allow_pickle=True)
