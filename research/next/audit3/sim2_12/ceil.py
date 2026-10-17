import cv2, numpy as np, sys, json
p=sys.argv[1]
cap=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
bg=np.median(np.stack(fr[36:]+fr[1:12]),axis=0)
# plane centres from blob
cents={}
for i in range(15,34):
    d=fr[i]-bg; m=(d>25).astype(np.uint8); m[750:]=0; m[:250]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); cents[i]=cen[k]
acc=np.zeros((400,1200),np.float32); cnt=0
prof=[]
for i in range(16,33):
    cx,cy=cents[i]
    d=cv2.GaussianBlur(fr[i]-bg,(15,15),0)
    x0=int(round(cx))-600
    if x0<0 or x0+1200>1920: 
        pass
    sub=np.zeros((400,1200),np.float32)
    xa=max(x0,0); xb=min(x0+1200,1920)
    sub[:,xa-x0:xb-x0]=d[0:400,xa:xb]
    acc+=sub; cnt+=1
    # ceiling region y<170: find darkest column-band centroid
    reg=d[60:170,:].copy()
    reg[:, 1650:]=0
    colmean=reg.mean(axis=0)
    w=np.clip(-colmean,0,None); 
    xc=(w*np.arange(1920)).sum()/w.sum()
    rowmean=d[40:175, int(cx)-150:int(cx)+150].mean(axis=1)
    ry=np.argmin(cv2.GaussianBlur(rowmean.reshape(-1,1),(1,9),0).ravel())+40
    prof.append((i,round(cx,1),round(cy,1),round(xc,1),int(ry),round(float(colmean.min()),2)))
for r in prof: print(r)
acc/=cnt
img=np.clip(128+40*acc,0,255).astype(np.uint8)
cv2.imwrite(sys.argv[2],cv2.resize(img,None,fx=0.75,fy=0.75))
# row profile of the stacked shadow near plane x
rp=acc[:, 450:750].mean(axis=1)
print('stacked row profile y:val (every 10)', [(y,round(float(rp[y]),2)) for y in range(40,400,10)])
cp=acc[60:170,:].mean(axis=0)
print('stacked col profile x-offset:val', [(x-600,round(float(cp[x]),2)) for x in range(0,1200,50)])
