import cv2, numpy as np
c1=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0244.mp4')
c0=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0243.mp4')
a=np.loadtxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_10/simulation_0245_segmented_t245.csv',delimiter=',')
R=[];f=0
while True:
    ok1,i1=c1.read(); ok0,i0=c0.read()
    if not ok1 or not ok0: break
    d=np.abs(i1.astype(int)-i0.astype(int)).max(axis=2)
    band=d[1400:1600]
    m=(band>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    if n>1:
        i=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[i]
        R.append((f,cen[i][0],x,w,y+1400,h,ar))
    else: R.append((f,np.nan,np.nan,np.nan,np.nan,np.nan,0))
    f+=1
R=np.array(R,float)
ok=~np.isnan(R[:,1])
print('n',ok.sum(),'rabbit cx slope',np.polyfit(R[ok,0],R[ok,1],1)[0].round(3))
print('0244 cx every 6',R[::6,1].round(1))
print('0245s cx every 6',a[::6,13].round(1))
print('0244 w median',np.nanmedian(R[:,3]),'h median',np.nanmedian(R[:,5]))
print('cycle diffs',[round(R[k+13,1]-R[k,1],1) for k in (7,20,33,46)])
