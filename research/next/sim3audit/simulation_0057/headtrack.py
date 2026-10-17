import cv2, numpy as np, sys
vid = sys.argv[1]
r0,r1 = [int(v) for v in sys.argv[2].split(',')]  # head rows
x0,x1 = 0,420
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[r0:r1,x0:x1].astype(np.int16))
fr=np.array(fr)
bg=np.median(fr,axis=0)
res=[]
for i,f in enumerate(fr):
    d=np.abs(f-bg).max(axis=2).astype(float)
    prof=(d>25).sum(axis=0)  # columns count
    cols=np.where(prof>=3)[0]
    # largest contiguous run
    if len(cols)==0: print(i,'none'); continue
    runs=np.split(cols, np.where(np.diff(cols)>3)[0]+1)
    runs=sorted(runs,key=len)[::-1]
    r=runs[0]
    w=prof[r[0]:r[-1]+1].astype(float)
    cx=(np.arange(r[0],r[-1]+1)*w).sum()/w.sum()
    print(i,'L',r[0],'R',r[-1],'W',r[-1]-r[0]+1,'cx %.2f'%cx, 'nruns',len(runs))
