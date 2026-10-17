import cv2, numpy as np, sys, json
c=sys.argv[1]; thr=float(sys.argv[2]) if len(sys.argv)>2 else 25
BG={'0085':[(0,1700,0),(1700,1920,71)],'0086':[(0,1920,71)],'0087':[(0,780,53),(780,1800,0),(1800,1920,53)]}
cap=cv2.VideoCapture(f'data/QuantiPhy/simulation_{c}.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
N=len(fr)
bg=np.zeros_like(fr[0])
for a,b,k in BG[c]: bg[:,a:b]=fr[k][:,a:b]
res=[]
for i,f in enumerate(fr):
    d=(np.abs(f-bg)>thr).astype(np.uint8)
    d=cv2.morphologyEx(d,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(d)
    objs=[]
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<150: continue
        objs.append(dict(x0=int(x),x1=int(x+w-1),y0=int(y),y1=int(y+h-1),area=int(a),cx=float(cen[k][0]),cy=float(cen[k][1])))
    res.append(objs)
json.dump(res,open(f'research/next/audit3/sim2_13/cartrack_{c}_{int(thr)}.json','w'))
for i in range(0,N,1):
    print(i, [(o['x0'],o['x1'],o['y0'],o['y1'],o['area']) for o in sorted(res[i],key=lambda o:-o['area'])[:3]])
