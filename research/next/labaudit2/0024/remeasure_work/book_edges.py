import cv2,numpy as np,sys
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
v=sys.argv[1] if len(sys.argv)>1 else 'captured_0024x'
img=cv2.imread(f'{W}/{v}_medA.png')
g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(float)
hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(int)
def subpix_edge(profile,thr):
    # first crossing of thr with linear interpolation
    for i in range(1,len(profile)):
        if (profile[i-1]-thr)*(profile[i]-thr)<=0 and profile[i]!=profile[i-1]:
            return i-1+(thr-profile[i-1])/(profile[i]-profile[i-1])
    return None
bg=g[300:340,700:880].mean() if v.endswith('x') else None
print('bg level',bg)
# back edge: column profiles top->down, book is bright vs dark/blurred bg
back=[]
for x in range(764,836,2):
    p=g[335:372,x]; lo=np.median(g[330:340,x]); hi=np.median(g[360:368,x]); e=subpix_edge(p,(lo+hi)/2)
    if e is not None: back.append((x,335+e))
left=[]
for y in range(357,377):
    p=g[y,700:780]; lo=np.median(g[y,695:705]); hi=np.median(g[y,770:780]); e=subpix_edge(p,(lo+hi)/2)
    if e is not None: left.append((700+e,y))
front=[]
for x in range(728,800,2):
    p=g[372:392,x]; i=np.argmin(p); 
    # parabola refine
    if 0<i<len(p)-1:
        d=(p[i-1]-p[i+1])/(2*(p[i-1]-2*p[i]+p[i+1])); front.append((x,372+i+d))
def fit(P,vertical=False):
    P=np.array(P)
    for it in range(3):
        if vertical: A=np.c_[P[:,1],np.ones(len(P))]; yv=P[:,0]
        else: A=np.c_[P[:,0],np.ones(len(P))]; yv=P[:,1]
        k,b=np.linalg.lstsq(A,yv,rcond=None)[0]; r=yv-(A@[k,b])
        keep=np.abs(r)<max(0.7,2.5*r.std()); P=P[keep]
    return k,b,r.std(),len(P)
kb,bb,sb,nb=fit(back); kl,bl,sl,nl=fit(left,vertical=True); kf,bf,sf,nf=fit(front)
print('back y=%.4f x+%.2f sd %.2f n %d'%(kb,bb,sb,nb))
print('left x=%.4f y+%.2f sd %.2f n %d'%(kl,bl,sl,nl))
print('front(dark line) y=%.4f x+%.2f sd %.2f n %d'%(kf,bf,sf,nf))
# corners
def ix_h_v(k,b,kv,bv):  # y=kx+b, x=kv y+bv
    y=(k*bv+b)/(1-k*kv); return np.array([kv*y+bv,y])
BL=ix_h_v(kb,bb,kl,bl); FLd=ix_h_v(kf,bf,kl,bl)
print('BL',np.round(BL,2),'FL(dark line)',np.round(FLd,2))
np.save(f'{W}/{v}_bookedges.npy',np.array([[kb,bb],[kl,bl],[kf,bf]]))
