import cv2, numpy as np, sys
vid = sys.argv[1]
x0,x1,y0,y1 = [int(v) for v in sys.argv[2].split(',')]   # ROI in full-res pixels
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[y0:y1,x0:x1].astype(np.int16))
fr=np.array(fr)
bg=np.median(fr,axis=0)
for i,f in enumerate(fr):
    d=np.abs(f-bg).max(axis=2)
    m=(d>30).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    ys,xs=np.where(lab==k)
    top=ys.min(); bot=ys.max(); h=bot-top
    up = ys < top+0.35*h
    tor = (ys>top+0.15*h)&(ys<top+0.45*h)
    print(i, 'top',top+y0,'bot',bot+y0,'xmin',xs.min()+x0,'xmax',xs.max()+x0,'upcx %.2f'%(xs[up].mean()+x0),'torcx %.2f'%(xs[tor].mean()+x0),'area',len(xs))
