import cv2,numpy as np,sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work')
import rect
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
v=sys.argv[1] if len(sys.argv)>1 else 'captured_0023x'
img=cv2.imread(f'{W}/{v}_medA.png'); g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(float)
hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(float); S=hsv[...,1]
def cross(p,thr):
    for i in range(1,len(p)):
        if (p[i-1]-thr)*(p[i]-thr)<=0 and p[i]!=p[i-1]: return i-1+(thr-p[i-1])/(p[i]-p[i-1])
# back edge: gray step from black
back=[(x,340+cross(g[340:365,x],100)) for x in range(545,640,2)]
# front dark line: min in window 376..384
front=[]
for x in range(545,640,2):
    p=g[376:385,x]; i=int(np.argmin(p))
    if 0<i<len(p)-1:
        den=p[i-1]-2*p[i]+p[i+1]; front.append((x,376+i+(p[i-1]-p[i+1])/(2*den)))
# left/right edges: saturation half-level crossing, rows 352..378
left=[];right=[]
for y in range(353,378):
    s=cv2.GaussianBlur(S,(3,3),0)[y]
    plateau=np.median(s[548:635]); 
    l=cross(s[515:560],plateau/2); r=cross(s[635:675][::-1],plateau/2)
    if l is not None: left.append((515+l,y))
    if r is not None: right.append((674-r,y))
def fitl(P,vert=False):
    P=np.array(P,float)
    for it in range(3):
        A=np.c_[P[:,1] if vert else P[:,0],np.ones(len(P))]; yv=P[:,0] if vert else P[:,1]
        k,b=np.linalg.lstsq(A,yv,rcond=None)[0]; r=yv-A@[k,b]; keep=np.abs(r)<max(0.7,2.5*r.std()); P=P[keep]
    return k,b,r.std()
kb,bb,sb=fitl(back); kf,bf,sf=fitl(front); kl,bl,sl=fitl(left,True); kr,br,sr=fitl(right,True)
print(v,'back y=%.4fx+%.2f sd%.2f | front y=%.4fx+%.2f sd%.2f | left x=%.3fy+%.1f sd%.2f | right x=%.3fy+%.1f sd%.2f'%(kb,bb,sb,kf,bf,sf,kl,bl,sl,kr,br,sr))
def ix(kh,bh,kv,bv): y=(kh*bv+bh)/(1-kh*kv); return np.array([kv*y+bv,y])
C=np.array([ix(kf,bf,kl,bl),ix(kf,bf,kr,br),ix(kb,bb,kr,br),ix(kb,bb,kl,bl)])
print('book corners FL FR BR BL',np.round(C,2))
np.save(f'{W}/{v}_bookcorners.npy',C)
