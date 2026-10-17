import cv2, numpy as np, sys
v=sys.argv[1]
bg=cv2.imread(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/bg_{v}.png').astype(float)
def meas(name,x0,y0,x1,y1):
    r=bg[y0:y1,x0:x1]
    border=np.concatenate([r[:3].reshape(-1,3),r[-3:].reshape(-1,3),r[:,:3].reshape(-1,3),r[:,-3:].reshape(-1,3)])
    ref=np.median(border,axis=0)
    d=np.abs(r-ref).max(axis=2)
    for thr in (10,20,35):
        m=d>thr
        rows=np.where(m.sum(1)>=3)[0]; cols=np.where(m.sum(0)>=3)[0]
        # main contiguous
        def run(a):
            br=np.split(a,np.where(np.diff(a)>3)[0]+1); return max(br,key=len)
        rr=run(rows); cc=run(cols)
        print(name,'thr',thr,'x %d-%d (%d)'%(x0+cc[0],x0+cc[-1],cc[-1]-cc[0]+1),'y %d-%d (%d)'%(y0+rr[0],y0+rr[-1],rr[-1]-rr[0]+1))
    # half-max along central row/col using luminance difference
    return ref
meas('purple',1220,380,1460,500)
meas('green',310,540,550,660)
