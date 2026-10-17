import cv2, numpy as np, sys, json
p = sys.argv[1]; split=int(sys.argv[2]); thr=float(sys.argv[3])
cap = cv2.VideoCapture(p)
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(cv2.resize(f,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA))
bg=np.median(np.stack(fr[::3]),axis=0).astype(np.float32)
bg=cv2.resize(bg,(1920,1080),interpolation=cv2.INTER_LINEAR)
del fr
cap = cv2.VideoCapture(p)
res=[]
while True:
    ok,f=cap.read()
    if not ok: break
    d=np.sqrt(((f.astype(np.float32)-bg)**2).sum(axis=2))
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    out={}
    for name,(y0,y1) in (('top',(0,split)),('bot',(split,1080))):
        mm=np.zeros_like(m); mm[y0:y1]=m[y0:y1]
        n,lab,st,cen=cv2.connectedComponentsWithStats(mm)
        if n<2: out[name]=None; continue
        k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
        sel=[j for j in range(1,n) if st[j][4]>=6 and st[j][0]>x-40 and st[j][0]+st[j][2]<x+w+40 and st[j][1]>y-40 and st[j][1]+st[j][3]<y+h+40]
        ys,xs=np.nonzero(np.isin(lab,sel))
        out[name]=[int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())]
    res.append(out)
json.dump(res,open(sys.argv[4],'w'))
for i in [1,2,12,23,24,36,47,48,60,71]:
    o=res[i]; s=[]
    for k in ('top','bot'):
        b=o[k]; s.append(f"{k} x{b[0]}-{b[1]} L{b[1]-b[0]+1} y{b[2]}-{b[3]} W{b[3]-b[2]+1} c({(b[0]+b[1])/2:.1f},{(b[2]+b[3])/2:.1f})" if b else k+' none')
    print(i,' | '.join(s))
