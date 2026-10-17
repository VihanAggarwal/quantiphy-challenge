import cv2, numpy as np, json
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0012.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f)
bg=cv2.imread('bg12.png').astype(int)
res=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(int)-bg).sum(2); m=(d>50).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # choose component with darkest mean (bird), largest area among dark
    best=None
    for k in range(1,n):
        if st[k,4]<500: continue
        mean=f[lab==k].mean()
        if best is None or mean<best[1]: best=(k,mean)
    k=best[0]; x,y,w,h,a=st[k]
    res.append((i,int(x),int(y),int(w),int(h),int(a),round(best[1],1)))
for r in res: print(r)
json.dump(res,open('s12box.json','w'))
