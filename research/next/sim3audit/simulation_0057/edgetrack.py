# subpixel left/right silhouette edges of the person in a row band, from background-difference profile
import cv2, numpy as np, sys
vid = sys.argv[1]; r0,r1=[int(v) for v in sys.argv[2].split(',')]
x0,x1=0,420
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[r0:r1,x0:x1].astype(np.float32))
fr=np.array(fr); bg=np.median(fr,axis=0)
out=[]
for i,f in enumerate(fr):
    d=np.abs(f-bg).max(axis=2)
    occ = (d>25).astype(float)
    prof = occ.mean(axis=0)          # fraction of rows covered, per column
    cols=np.where(prof>0.3)[0]
    if len(cols)==0: out.append((i,np.nan,np.nan)); continue
    runs=np.split(cols, np.where(np.diff(cols)>3)[0]+1); r=max(runs,key=len)
    a,b=r[0],r[-1]
    # subpixel: 50% crossing of profile relative to plateau
    pl = np.median(prof[a:b+1])
    def cross(j0,step):
        j=j0
        while 0<j<len(prof)-1 and prof[j]>0.5*pl: j-=step
        # interpolate between j and j+step
        p0,p1=prof[j],prof[j+step]
        return j + step*(0.5*pl-p0)/(p1-p0+1e-9)
    L=cross(a,1); R=cross(b,-1)
    out.append((i,L,R))
for i,L,R in out: print(i,'%.2f %.2f %.2f'%(L,R,R-L))
