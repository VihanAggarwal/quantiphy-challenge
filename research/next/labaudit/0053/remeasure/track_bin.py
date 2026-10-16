import cv2,numpy as np
fr=np.load('captured_0053x.npy')
rows=[]
for i in range(len(fr)):
    f=fr[i].astype(int)
    b,g,r=f[...,0],f[...,1],f[...,2]
    green=(g>200)&(r<80)&(b<80)
    m=(~green).astype(np.uint8)
    m[680:,1000:]=0  # watermark
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # bin = component with blue colour, largest except ball etc: choose component with max area excluding known static ones
    best=None
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<1500: continue
        mm=lab==k
        blue=np.mean((b[mm]>r[mm]+30))
        if blue>0.3 and (best is None or a>best[1]): best=(k,a)
    k=best[0]; x,y,w,h,a=st[k]
    mm=(lab==k).astype(np.uint8)
    cs,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    rows.append((i,cen[k][0],cen[k][1],x,y,w,h,a,x+w/2,y+h/2))
np.save('bin_track_x.npy',np.array(rows))
for rr in rows: print('%2d cen (%.1f,%.1f) bbox %d %d %d %d area %d bbc (%.1f,%.1f)'%rr)
