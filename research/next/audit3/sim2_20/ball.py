import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0116_segmented.mp4')
rows=[]; i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=f.astype(int)
    nonw=(g.min(axis=2)<215)
    # ball region: exclude doors (x 640..820 and y>800); ball is dark-brown
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    yellow=(hsv[...,0]>15)&(hsv[...,0]<40)&(hsv[...,1]>80)
    m=nonw&~yellow
    m[:, :900]=False if i<0 else m[:, :900]
    # connected components; choose the largest dark blob outside door boxes
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    best=None
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<200: continue
        if 640<=x<=830 and y>780: continue
        if best is None or a>best[4]: best=(x,y,w,h,a)
    rows.append((i,)+tuple(best) if best else (i,np.nan,np.nan,np.nan,np.nan,np.nan))
    i+=1
r=np.array(rows,dtype=float)
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_20/s116_ball.txt',r,fmt='%.1f')
for x in r: print(' '.join('%.0f'%t for t in x))
