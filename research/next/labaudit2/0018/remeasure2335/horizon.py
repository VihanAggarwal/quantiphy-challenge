import cv2, numpy as np
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
o=np.load(S+'o.npy')
# temporal median of the original render to suppress people motion a bit
g=cv2.cvtColor(o[48],cv2.COLOR_BGR2GRAY)
# Sample: for given columns, find strongest vertical gradient (dark baseboard top edge / panel top edge) in a y-window
def trace(cols, y0, y1, sign):
    pts=[]
    gy=cv2.Sobel(cv2.GaussianBlur(g.astype(float),(5,5),0),cv2.CV_64F,0,1,ksize=5)
    for c in cols:
        seg=sign*gy[y0(c):y1(c),c]
        k=np.argmax(seg); pts.append((c,y0(c)+k,seg[k]))
    return np.array(pts,float)
def fitline(p):
    A=np.c_[p[:,0],np.ones(len(p))]; m,b=np.linalg.lstsq(A,p[:,1],rcond=None)[0]
    res=p[:,1]-(m*p[:,0]+b); return m,b,np.abs(res).max()
# left wall baseboard: bright wall above, dark baseboard below -> negative gradient (bright to dark going down)
lb=trace(range(10,330,10), lambda c:int(560-0.24*c), lambda c:int(620-0.24*c), -1)
print('left base pts',lb[:,:2].astype(int).tolist())
# back wall baseboard top edge between x=560 and 840 (avoid tripods)
bb=trace(list(range(560,700,10))+list(range(720,840,10)), lambda c:int(470+0.12*(c-450)), lambda c:int(510+0.12*(c-450)), -1)
print('back base pts',bb[:,:2].astype(int).tolist())
# left wall top edge (wall panel top vs bright ceiling): bright above, darker panel below
lt=trace(range(10,330,10), lambda c:int(40+0.25*c), lambda c:int(100+0.25*c), -1)
print('left top pts',lt[:,:2].astype(int).tolist())
bt=trace(list(range(470,580,10)), lambda c:150, lambda c:200, -1)
print('back top pts',bt[:,:2].astype(int).tolist())
for name,p in [('lb',lb),('bb',bb),('lt',lt),('bt',bt)]:
    print(name, fitline(p))
def inter(l1,l2):
    m1,b1=l1[:2]; m2,b2=l2[:2]; x=(b2-b1)/(m1-m2); return x, m1*x+b1
L1=fitline(lb); L2=fitline(lt); B1=fitline(bb); B2=fitline(bt)
vp1=inter(L1,L2); vp2=inter(B1,B2)
print('VP left-wall dir',vp1,' VP back-wall dir',vp2)
m=(vp2[1]-vp1[1])/(vp2[0]-vp1[0]); print('horizon at x=640: %.1f  slope %.4f'%(vp1[1]+m*(640-vp1[0]),m))
