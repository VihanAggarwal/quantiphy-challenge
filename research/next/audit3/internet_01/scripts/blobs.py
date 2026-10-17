import cv2, numpy as np, sys, json
# generic: background-median diff blobs within a corridor; prints per-frame blobs
V=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6]); thr=int(sys.argv[6]) if len(sys.argv)>6 else 30
c=cv2.VideoCapture(V); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[y0:y1,x0:x1].copy())
F=np.stack(fr); bg=np.median(F[::2],axis=0).astype(np.uint8)
out=[]
for i,f in enumerate(F):
    d=cv2.absdiff(f,bg).max(axis=2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<40: continue
        out.append([i,int(x+x0),int(y+y0),int(w),int(h),int(a),float(cen[k][0]+x0),float(cen[k][1]+y0)])
json.dump(out,open(sys.argv[7],'w'))
cv2.imwrite(sys.argv[7].replace('.json','_bg.png'),bg)
print(len(F),len(out))
