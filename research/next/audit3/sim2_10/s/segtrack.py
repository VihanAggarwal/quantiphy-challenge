import cv2, numpy as np, sys, csv
c=sys.argv[1]; thr=int(sys.argv[2]) if len(sys.argv)>2 else 235
ymin=int(sys.argv[3]) if len(sys.argv)>3 else 0
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
rows=[]; f=0
while True:
    ok,im=cap.read()
    if not ok: break
    g=im.astype(int)
    m=((g.min(axis=2)<thr)).astype(np.uint8)
    m[:ymin]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    comps=[(st[i,4],st[i,0],st[i,1],st[i,2],st[i,3],cen[i,0],cen[i,1]) for i in range(1,n) if st[i,4]>400]
    comps.sort(reverse=True)
    big=comps[0]; small=[x for x in comps[1:]]
    r=[f]+list(big[1:])
    if small:
        s=small[0]; r+=list(s[1:])
    else: r+=[np.nan]*6
    rows.append(r); f+=1
w=csv.writer(open(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_10/{c}_seg.csv','w'))
w.writerow(['f','ax','ay','aw','ah','acx','acy','rx','ry','rw','rh','rcx','rcy'])
w.writerows(rows)
a=np.array(rows,float)
print('bg sample', cap.get(0))
for k,nm in [(3,'aw'),(4,'ah'),(9,'rw'),(10,'rh')]:
    v=a[:,k]; v=v[~np.isnan(v)]
    print(nm,'median',np.median(v),'mean',v.mean().round(1),'min',v.min(),'max',v.max(), 'p25,p75',np.percentile(v,[25,75]))
f=a[:,0]
for k,nm in [(5,'acx'),(11,'rcx')]:
    v=a[:,k]; ok=~np.isnan(v)
    p=np.polyfit(f[ok],v[ok],1); print(nm,'slope px/f',p[0].round(3))
