import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0246.mp4'
c=cv2.VideoCapture(V); F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
F=np.array(F); n=len(F)
def trk(box,ref,vguess=9.6,win=50,chain=0):
    x0,x1,y0,y1=box; w=x1-x0; h=y1-y0
    T=F[ref][y0:y1,x0:x1]; xs=[];sc=[]
    for i in range(n):
        px=x0+vguess*(i-ref)
        a=int(max(0,px-win)); b=int(min(F.shape[2],px+w+win))
        R=cv2.matchTemplate(F[i][y0-15:y1+15,a:b],T,cv2.TM_CCOEFF_NORMED)
        _,mv,_,ml=cv2.minMaxLoc(R); x,y=ml
        if 0<x<R.shape[1]-1:
            p,q,r=R[y,x-1],R[y,x],R[y,x+1]; den=p-2*q+r; dx=0.5*(p-r)/den if den!=0 else 0
        else: dx=0
        xs.append(a+x+dx-x0); sc.append(mv)
    xs=np.array(xs); fr=np.arange(n)
    return xs,np.array(sc)
fr=np.arange(75)
res={}
for ref in (0,37,74):
  print('--- ref',ref)
  off=int(round(9.6*ref))
  boxes={'rump':(470,560,520,620),'midback':(560,660,540,600),'shoulder':(660,760,535,605),'neck':(760,850,545,595),'head':(840,940,540,620),'tailtuft':(340,400,555,600),'hornL':(420,520,425,470)}
  for k,(x0,x1,y0,y1) in boxes.items():
    b=(x0+off,x1+off,y0,y1)
    if b[1]>1920: continue
    xs,sc=trk(b,ref)
    p=np.polyfit(fr,xs,1); r=xs-np.polyval(p,fr)
    print('%-9s fit %.3f e2e %.3f rms %.1f minsc %.2f'%(k,p[0],(xs[-1]-xs[0])/74,r.std(),sc.min()))
    res[(ref,k)]=xs
np.savez('/tmp/claude-0/tr3.npz',**{'%d_%s'%k:v for k,v in res.items()}) if False else None
