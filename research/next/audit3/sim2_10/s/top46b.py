import cv2, numpy as np, sys
c='simulation_0246'; thr=int(sys.argv[1]) if len(sys.argv)>1 else 25
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
out=[];i=0
while True:
    ok,im=cap.read()
    if not ok: break
    sm=cv2.resize(im,None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA)
    bgs=np.dstack([cv2.medianBlur(sm[:,:,k],91) for k in range(3)])
    bg=cv2.resize(bgs,(im.shape[1],im.shape[0]),interpolation=cv2.INTER_LINEAR)
    d=np.abs(cv2.GaussianBlur(im,(3,3),0).astype(np.int16)-bg.astype(np.int16)).max(axis=2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    comps=sorted([(st[k,4],k) for k in range(1,n)],reverse=True)
    A=st[comps[0][1]]; ca=cen[comps[0][1]]
    R=None
    for a,k in comps[1:]:
        x,y,w,h,ar=st[k]
        if 400<ar<12000 and y+h<450 and y>200: R=(st[k],cen[k]); break
    row=[i,A[0],A[1],A[2],A[3],ca[0],ca[1]]
    row+= [R[0][0],R[0][1],R[0][2],R[0][3],R[1][0],R[1][1]] if R is not None else [np.nan]*6
    out.append(row)
    if i in (0,37,74):
        vis=im.copy(); vis[m>0]=(vis[m>0]*0.5+np.array([0,0,127])).astype(np.uint8)
        cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_10/png/m46_{i}.png',cv2.resize(vis,None,fx=0.5,fy=0.5))
    i+=1
a=np.array(out,float)
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_10/top46.csv',a,delimiter=',',fmt='%.2f',header='f,ax,ay,aw,ah,acx,acy,rx,ry,rw,rh,rcx,rcy')
t=a[:,0]
print('antelope w median',np.median(a[:,3]),'p10,p90',np.percentile(a[:,3],[10,90]),'h median',np.median(a[:,4]))
print('w every 6',a[::6,3])
for k,nm in [(5,'acx'),(1,'aleft')]:
    print(nm,'slope',np.polyfit(t,a[:,k],1)[0].round(3))
print('aright slope',np.polyfit(t,a[:,1]+a[:,3],1)[0].round(3))
ok=~np.isnan(a[:,11])
print('rabbit n',ok.sum(),'w median',np.nanmedian(a[:,9]),'p10,p90',np.nanpercentile(a[:,9],[10,90]),'h median',np.nanmedian(a[:,10]))
print('rcx slope',np.polyfit(t[ok],a[ok,11],1)[0].round(3))
print('rabbit w every 6',a[::6,9]); print('rabbit cx every 6',a[::6,11].round(1))
