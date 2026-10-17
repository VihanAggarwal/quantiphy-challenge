import cv2, sys, numpy as np, json
v=sys.argv[1]; thr=int(sys.argv[2]) if len(sys.argv)>2 else 30
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(f)
F=np.array(F)
bg=np.median(F[::2],axis=0).astype(np.uint8)
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/bg_{v}.png',bg)
out=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(int)-bg.astype(int)).max(axis=2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    bl=[]
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<150: continue
        bl.append([int(x),int(y),int(w),int(h),int(a),round(float(cen[k][0]),2),round(float(cen[k][1]),2)])
    out.append(bl)
json.dump(out,open(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/blobs_{v}.json','w'))
for i in (0,1,24,48,71):
    print(i,out[i])
