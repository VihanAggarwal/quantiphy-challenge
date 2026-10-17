import cv2, numpy as np, sys
vid=sys.argv[1]; r0,r1=[int(v) for v in sys.argv[2].split(',')]; x0,x1=[int(v) for v in sys.argv[3].split(',')]
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[r0:r1,x0:x1].astype(np.float32))
fr=np.array(fr); bg=np.median(fr,axis=0)
for i,f in enumerate(fr):
    d=np.abs(f-bg).max(axis=2)
    prof=(d>25).mean(axis=0)
    cols=np.where(prof>0.3)[0]
    if len(cols)==0: print(i,'nan nan nan'); continue
    runs=np.split(cols, np.where(np.diff(cols)>3)[0]+1); r=max(runs,key=len)
    a,b=r[0],r[-1]; pl=np.median(prof[a:b+1])
    def cross(j,step):
        while 0<j<len(prof)-1 and prof[j]>0.5*pl: j-=step
        p0,p1=prof[j],prof[j+step]; return j+step*(0.5*pl-p0)/(p1-p0+1e-9)
    L=cross(a,1)+x0; R=cross(b,-1)+x0
    rows=np.where((d>25).mean(axis=1)>0.05)[0]
    print(i,'%.2f %.2f %.2f'%(L,R,R-L), r0+rows.min() if len(rows) else -1)
