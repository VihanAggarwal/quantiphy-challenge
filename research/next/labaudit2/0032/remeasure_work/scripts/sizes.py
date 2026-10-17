import numpy as np, sys, cv2
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/scripts')
from geom import *
H=17.8
src='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0032.mp4'
cap=cv2.VideoCapture(src); fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
def maskc(img,kind):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(int)
    roi=np.zeros(hsv.shape[:2],bool); roi[380:520,440:1000]=True
    if kind=='w': m=(hsv[...,1]<60)&(hsv[...,2]>170)&roi
    else: m=(hsv[...,0]>20)&(hsv[...,0]<40)&(hsv[...,1]>120)&(hsv[...,2]>120)&roi
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n_,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); return cen[k],st[k]
def score(img,kind):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(float)
    if kind=='w': return (hsv[...,2]/255.0)*(1-hsv[...,1]/255.0)
    # yellow-ness: saturation*value with hue gate
    hue=hsv[...,0]; g=np.exp(-((hue-30)/8.0)**2)
    return g*hsv[...,1]/255.0*hsv[...,2]/255.0
def hm_width(p):
    mx=p.max(); mn=np.median(np.r_[p[:6],p[-6:]]); th=(mx+mn)/2
    idx=np.where(p>th)[0]; a=idx[0]; b=idx[-1]
    lo=a-1+(th-p[a-1])/(p[a]-p[a-1]); hi=b+(p[b]-th)/(p[b]-p[b+1])
    return lo,hi
for kind,D,frames in (('w',4.0,[5,10,15,20,36,38,40,42,44,46,48]),('y',6.7,[5,10,15,20,23,25,27,29,36,38,40])):
    for i in frames:
        (cxb,cyb),st=maskc(fr[i],kind)
        S=score(fr[i],kind)
        x0,y0=int(round(cxb)),int(round(cyb))
        half=40 if kind=='y' else 30
        best=0
        # max horizontal chord over rows near centre
        ws=[]
        for yy in range(y0-6,y0+7):
            p=S[yy,x0-half:x0+half+1]
            try:
                lo,hi=hm_width(p); ws.append((hi-lo,yy,(lo+hi)/2+x0-half))
            except Exception: pass
        ws=sorted(ws)[-3:]
        Wd=np.mean([w[0] for w in ws]); yrow=np.mean([w[1] for w in ws]); uc=np.mean([w[2] for w in ws])
        # vertical extent at column uc
        q=S[y0-half:y0+half+1,int(round(uc))-1:int(round(uc))+2].mean(1)
        lo,hi=hm_width(q); Hd=hi-lo
        # plane model range for centre at (uc, yrow)
        p=on_plane(uc,yrow,H-D/2); Rp=np.linalg.norm(p)
        print('%s f%02d blob=(%.1f,%.1f) maxchord W=%.1f at row %.1f, vert H=%.1f top %.1f | size-range f*D/W=%.1f  plane-range(centre row)=%.1f'%(kind,i,cxb,cyb,Wd,yrow,Hd,lo+y0-half,711*D/Wd,Rp))
