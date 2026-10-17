import cv2,numpy as np,sys
fn=sys.argv[1]
im=cv2.imread(fn).astype(float); im=cv2.GaussianBlur(im,(0,0),1.0)
def edge_line(chan,p0,p1,vrange,sign,win=7,name=''):
    a=(p1[0]-p0[0])/(p1[1]-p0[1]); b=p0[0]-a*p0[1]
    pts=[]
    for v in range(*vrange):
        xc=a*v+b; xs=np.arange(int(xc-win),int(xc+win)+1)
        row=chan[v,xs[0]-1:xs[-1]+2]
        d=(row[2:]-row[:-2])/2*sign
        i=np.argmax(d)
        if 0<i<len(d)-1:
            den=d[i-1]-2*d[i]+d[i+1]; off=0.5*(d[i-1]-d[i+1])/den if den!=0 else 0
            pts.append((xs[i]+off,v,d[i]))
    P=np.array(pts)
    keep=np.ones(len(P),bool)
    for it in range(5):
        A=np.c_[P[keep,1],np.ones(keep.sum())]; c=np.linalg.lstsq(A,P[keep,0],rcond=None)[0]
        r=P[:,0]-(c[0]*P[:,1]+c[1]); s=max(np.std(r[keep]),0.3); keep=np.abs(r)<2.5*s
    print(f'{name}: x = {c[0]:.4f} v + {c[1]:.2f}  rms {np.std(r[keep]):.3f} n={keep.sum()}/{len(P)}')
    return c
G=im[...,1]
cl=edge_line(G,(328.3,960),(175,1055),(958,1062,1),+1,name='inlay left (G rising)')
cr=edge_line(G,(1730,961.7),(1863.3,1050),(958,1062,1),-1,name='inlay right (G falling)')
VPv=(cr[1]-cl[1])/(cl[0]-cr[0]); print('VP of inlay sides v=',round(VPv,1),'x=',round(cl[0]*VPv+cl[1],1))
np.save(fn.replace('.png','_inlay.npy'),np.r_[cl,cr])
for v in [960,984,992,1001]: print(v,'width',round((cr[0]-cl[0])*v+cr[1]-cl[1],2))
