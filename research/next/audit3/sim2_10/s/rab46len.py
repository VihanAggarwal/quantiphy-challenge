import cv2, numpy as np
b=np.loadtxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_10/top46.csv',delimiter=',')
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0246.mp4')
W=[];WO=[];f=0
while True:
    ok,im=cap.read()
    if not ok: break
    cx=int(b[f,11]); cy=int(b[f,12])
    y0,y1,x0,x1=cy-70,cy+70,cx-110,cx+110
    cr=im[y0:y1,x0:x1]
    hsv=cv2.cvtColor(cr,cv2.COLOR_BGR2HSV).astype(int)
    sm=cv2.resize(im,None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA)
    bg=np.dstack([cv2.medianBlur(sm[:,:,k],91) for k in range(3)])
    bg=cv2.resize(bg,(im.shape[1],im.shape[0]))[y0:y1,x0:x1]
    hb=cv2.cvtColor(bg,cv2.COLOR_BGR2HSV).astype(int)
    orange=(hsv[:,:,1]-hb[:,:,1]>40)
    card=(hsv[:,:,2]-hb[:,:,2]>12)&(hsv[:,:,1]<=hb[:,:,1]+10)
    m=(orange|card).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    # keep components near center
    keep=np.zeros_like(m)
    for i in range(1,n):
        if st[i,4]>30 and abs(cen[i,0]-110)<80 and abs(cen[i,1]-70)<50: keep[lab==i]=1
    cols=np.where(keep.sum(0)>0)[0]; W.append(cols.max()-cols.min()+1 if len(cols) else np.nan)
    oc=np.where((orange&(keep>0)).sum(0)>0)[0]; WO.append(oc.max()-oc.min()+1 if len(oc) else np.nan)
    if f in (25,55):
        v=cr.copy(); v[keep>0]=(v[keep>0]*0.4+np.array([0,0,150])).astype(np.uint8)
        cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_10/png/rab46mask_{f}.png',cv2.resize(v,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
    f+=1
W=np.array(W,float); WO=np.array(WO,float)
print('rabbit top width (orange+card) median',np.nanmedian(W),'mean',np.nanmean(W).round(1),'p10,p90',np.nanpercentile(W,[10,90]))
print('orange only median',np.nanmedian(WO))
print('every 5',W[::5])
