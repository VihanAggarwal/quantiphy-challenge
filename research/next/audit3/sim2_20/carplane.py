import cv2, numpy as np, sys
v=sys.argv[1]; split=int(sys.argv[2])  # y split between plane (above) and car (below)
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%v)
F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.int16))
bg=np.median(np.array(F[::4]+[F[-1]]),axis=0).astype(np.int16)
# background: use uniform color estimate: mode of first frame border
bgval=np.median(F[0][0:50,:])
print('frames',len(F),'bg',bgval)
res=[]
for i,f in enumerate(F):
    m=np.abs(f-bgval)>12
    out=[i]
    for (y0,y1) in [(0,split),(split,1080)]:
        sub=m[y0:y1]
        cols=np.nonzero(sub.sum(axis=0)>=2)[0]; rows=np.nonzero(sub.sum(axis=1)>=2)[0]
        if len(cols)==0: out+= [np.nan]*4; continue
        out+=[cols.min(), cols.max(), rows.min()+y0, rows.max()+y0]
    res.append(out)
r=np.array(res,dtype=float)
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_20/%s_bb.txt'%v,r,fmt='%.1f')
for x in r[::4]: print(' '.join('%.0f'%t for t in x))
