import cv2, numpy as np, json, sys
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work/'
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0311.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
F=np.stack(fr)  # 72x1440x2560x3
bg=np.median(F[::2],axis=0).astype(np.uint8)
cv2.imwrite(W+'bg.png',bg)
info=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(np.int16)-bg.astype(np.int16)).max(axis=2)
    m=(d>30).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
        info.append(dict(i=i,x=int(x),y=int(y),w=int(w),h=int(h),area=int(a),cx=float(cen[k][0]),cy=float(cen[k][1])))
    else: info.append(dict(i=i,area=0))
    print(info[-1])
json.dump(info,open(W+'mask_stats.json','w'))
