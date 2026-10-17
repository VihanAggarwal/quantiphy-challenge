import cv2, numpy as np
c='simulation_0246'
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(cv2.GaussianBlur(im,(3,3),0))
f0=fr[0].astype(np.int16); f74=fr[-1].astype(np.int16)
bg=f74.copy(); bg[:,930:]=f0[:,930:]; bg[270:410,930:1040]=f74[270:410,930:1040]
thr=30
out=[]
for i,im in enumerate(fr):
    d=np.abs(im.astype(np.int16)-bg).max(axis=2)
    m=(d>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    comps=sorted([(st[k,4],k) for k in range(1,n)],reverse=True)
    A=st[comps[0][1]]; ca=cen[comps[0][1]]
    R=None
    for a,k in comps[1:]:
        x,y,w,h,ar=st[k]
        if 400<ar<8000 and y+h<450: R=(st[k],cen[k]); break
    row=[i,A[0],A[1],A[2],A[3],ca[0],ca[1]]
    row+= [R[0][0],R[0][1],R[0][2],R[0][3],R[1][0],R[1][1]] if R is not None else [np.nan]*6
    out.append(row)
    if i in (0,37,74):
        vis=fr[i].copy(); vis[m>0]=(vis[m>0]*0.5+np.array([0,0,127])).astype(np.uint8)
        cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_10/png/m46_{i}.png',cv2.resize(vis,None,fx=0.5,fy=0.5))
a=np.array(out,float)
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_10/top46.csv',a,delimiter=',',fmt='%.2f')
t=a[:,0]
print('antelope w median',np.median(a[:,3]),'p10,p90',np.percentile(a[:,3],[10,90]),'h median',np.median(a[:,4]))
print('w every 6',a[::6,3])
for k,nm in [(5,'acx'),(1,'aleft')]:
    print(nm,'slope',np.polyfit(t,a[:,k],1)[0].round(3))
print('aright slope',np.polyfit(t,a[:,1]+a[:,3],1)[0].round(3))
ok=~np.isnan(a[:,11])
print('rabbit n',ok.sum(),'w median',np.nanmedian(a[:,9]),'p10,p90',np.nanpercentile(a[:,9],[10,90]),'h median',np.nanmedian(a[:,10]))
print('rcx slope',np.polyfit(t[ok],a[ok,11],1)[0].round(3))
print('rabbit w every 6',a[::6,9])
