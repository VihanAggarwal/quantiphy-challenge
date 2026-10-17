import cv2, numpy as np
def frame(v,i):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=c.read(); return f.astype(float)
def bg(v): return cv2.imread(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/bg_{v}.png').astype(float)
def extent(f,b,axis,lo,hi,a,bb,thr):
    # within band [lo,hi] along the other axis, find extent along 'axis' over window a..bb (max over lines)
    d=np.abs(f-b).max(axis=2)
    best=0;
    for k in range(lo,hi):
        p=d[k,a:bb] if axis=='x' else d[a:bb,k]
        idx=np.where(p>thr)[0]
        if len(idx)==0: continue
        # contiguous main run
        br=np.split(idx,np.where(np.diff(idx)>2)[0]+1); r=max(br,key=len)
        best=max(best,r[-1]-r[0]+1)
    return best
for v in ['simulation_0068','simulation_0070','simulation_0071','simulation_0075']:
    b=bg(v)
    f0=frame(v,0); f71=frame(v,71)
    # yellow vertical at f0: x 945-1040, rows 750-955 ; width along x
    w0=[extent(f0,b,'x',760,950,940,1045,t) for t in (20,35,50)]
    l0=[extent(f0,b,'y',960,1025,735,970,t) for t in (20,35,50)]
    w71=[extent(f71,b,'y',1275,1475,585,690,t) for t in (20,35,50)]
    l71=[extent(f71,b,'x',600,675,1255,1490,t) for t in (20,35,50)]
    print(v,'yellow f0 width',w0,'len',l0,' f71 width',w71,'len',l71)
for v in ['simulation_0069','simulation_0073']:
    b=bg(v); f=frame(v,40)
    w=[extent(f,b,'x',520,760,775,890,t) for t in (20,35,50)]
    print(v,'van f40 max width (rows 520-760)',w)
