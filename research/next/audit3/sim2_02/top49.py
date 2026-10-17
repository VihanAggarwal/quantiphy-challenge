import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0249.mp4'); F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
F=np.array(F)
# background: per-pixel 85th percentile of brightness frames (animals mostly darker), fall back
gray=F.astype(np.int16).sum(3)
idx=np.argsort(gray,axis=0)[int(0.85*len(F))]
bg=np.take_along_axis(F,idx[None,:,:,None].repeat(3,3),axis=0)[0].astype(np.int16)
bg=cv2.medianBlur(bg.astype(np.uint8),21).astype(np.int16)
rows=[]
for i in range(len(F)):
    d=np.abs(F[i].astype(np.int16)-bg).sum(2)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    L=sorted([(int(st[k,0]),int(st[k,1]),int(st[k,0]+st[k,2]-1),int(st[k,1]+st[k,3]-1),int(st[k,4]),round(cen[k,0],1),round(cen[k,1],1)) for k in range(1,n) if st[k,4]>200],key=lambda t:t[6])
    rows.append(L)
    if i%8==0 or i>=47: print(i,L)
    if i==24:
        vis=F[i].copy(); vis[m>0]=(vis[m>0]*0.5+np.array([0,0,128])).astype(np.uint8); cv2.imwrite('mask_0249_24.png',cv2.resize(vis[200:700,500:1400],None,fx=0.7,fy=0.7))
json.dump(rows,open('top49.json','w'))
