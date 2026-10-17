import cv2, numpy as np, json, sys
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg=np.median(np.stack(fr),axis=0).astype(np.float32) if sys.argv[3]=='all' else np.median(np.stack(fr[0:12]),axis=0).astype(np.float32)
w=np.array([0.114,0.587,0.299],np.float32)
for i in frames:
    f=fr[i].astype(np.float32)
    dB=bg[...,0]-f[...,0]; dY=bg@w-f@w
    m=(dB>30).astype(np.uint8); n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,ww,hh,a=st[k]
    W=np.clip(dB[y-4:y+hh+4,x-4:x+ww+4],0,None); yy,xx=np.mgrid[y-4:y+hh+4,x-4:x+ww+4]
    cx=(W*xx).sum()/W.sum(); cy=(W*yy).sum()/W.sum()
    r=np.arange(0,22,0.1); angs=np.radians(np.arange(0,360,3))
    PX=(cx+np.cos(angs)[:,None]*r).astype(np.float32); PY=(cy+np.sin(angs)[:,None]*r).astype(np.float32)
    pB=cv2.remap(dB,PX,PY,cv2.INTER_LINEAR).mean(0); pY=cv2.remap(dY,PX,PY,cv2.INTER_LINEAR)
    # azimuthally averaged blue profile and per-angle luma
    def edge(p,inner):
        half=inner/2; j=np.where((r>6)&(p<half))[0]
        if len(j)==0: return np.nan
        j=j[0]; return r[j-1]+(p[j-1]-half)/(p[j-1]-p[j])*0.1
    eB=edge(pB,np.median(pB[r<6]))
    pYm=np.median(pY,0)
    eY=edge(pYm,np.median(pYm[(r>3)&(r<7)]))
    print(f'{vid} f{i} c=({cx:.1f},{cy:.1f}) blue-edge radius={eB:.2f} (D={2*eB:.2f})  luma-median-edge radius={eY:.2f} (D={2*eY:.2f})')
    print('   blue prof r=8..16:',' '.join(f'{v:.0f}' for v in pB[80:161:5]))
    print('   luma prof r=8..16:',' '.join(f'{v:.0f}' for v in pYm[80:161:5]))
