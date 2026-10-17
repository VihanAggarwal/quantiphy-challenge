import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0061.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
P='research/next/audit3/internet_11/png/'
# body x-ranges per frame from the diff profile run (body run) earlier
runs={36:(278,431),38:(278,432),39:(319,470),40:(406,581),41:(543,718),42:(718,872),43:(927,1068),44:(1162,1305)}
tiles=[]
for i,(x0,x1) in runs.items():
    g=cv2.cvtColor(fr[i],cv2.COLOR_BGR2GRAY).astype(np.float32)
    gs=cv2.GaussianBlur(g,(0,0),3)
    xc=(x0+x1)//2
    band=gs[:,max(0,xc-15):xc+15].mean(axis=1)
    # body is bright: find contiguous run above threshold around y~530
    thr=0.5*(np.percentile(band[300:800],95)+np.median(band[300:800]))
    ys=np.where(band>thr)[0]; ys=ys[(ys>300)&(ys<800)]
    runs_y=np.split(ys,np.where(np.diff(ys)>3)[0]+1)
    rr=max(runs_y,key=len)
    # also max extent over several columns
    ext=[]
    for xx in range(x0+10,x1-10,6):
        b=gs[:,xx-2:xx+3].mean(axis=1)
        yy=np.where(b>thr)[0]; yy=yy[(yy>300)&(yy<800)]
        if len(yy)==0: continue
        rs=np.split(yy,np.where(np.diff(yy)>3)[0]+1); r=max(rs,key=len)
        ext.append(r[-1]-r[0]+1)
    print(i,'centre col %d run %d-%d len %d thr %.0f'%(xc,rr[0],rr[-1],len(rr),thr),'max col extent',max(ext) if ext else None, 'p90',int(np.percentile(ext,90)) if ext else None)
    c=fr[i][380:700,max(0,xc-170):xc+170].copy()
    c=cv2.resize(c,(340,320)); cv2.putText(c,str(i),(5,20),0,0.6,(0,0,255),2)
    for y in range(0,320,20): cv2.line(c,(0,y),(8 if y%100 else 16,y),(0,255,0),1)
    tiles.append(c)
cv2.imwrite(P+'a61_w.png',np.vstack([np.hstack(tiles[:4]),np.hstack(tiles[4:])]))
