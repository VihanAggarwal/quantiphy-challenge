import cv2,numpy as np,sys,json
v=sys.argv[1]; thr=float(sys.argv[2]); r0=int(sys.argv[3]); r1=int(sys.argv[4]); out=sys.argv[5]
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(cv2.GaussianBlur(im,(3,3),0)[r0-60:r1+60])
F=np.array(F)
bg=np.median(F,axis=0).astype(np.float32)
res={}
for i,im in enumerate(F):
    d=np.abs(im.astype(np.float32)-bg).max(axis=2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); mk=(lab==k)[60:60+(r1-r0)]
    L=[];R=[]
    for r in range(mk.shape[0]):
        nz=mk[r].nonzero()[0]
        if len(nz): L.append(nz.min()); R.append(nz.max())
    if len(L)<(r1-r0)*0.8: continue
    l=np.median(L); rr=np.median(R)
    if l<=1 or rr>=1918: continue
    res[i]=(float(l),float(rr))
    print(i,l,rr,(l+rr)/2,rr-l)
json.dump(res,open(out,'w'))
