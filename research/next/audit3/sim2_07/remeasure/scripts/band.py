import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0254.mp4')
fr=[]
for i in range(12):
    ok,f=c.read(); fr.append(f)
bg=np.median(np.stack(fr),axis=0).astype(np.float32)
Y=bg@np.array([0.114,0.587,0.299],np.float32)
th=np.radians(44.224); d=np.array([np.cos(th),np.sin(th)]); n=np.array([-d[1],d[0]])  # n points down-left
# reference point on ball path (frame 30 centre)
p0=np.array([649.6,331.56])
for s in range(-450,900,75):
    c0=p0+s*d
    r=np.arange(-80,80,0.5)
    px=(c0[0]+r*n[0]).astype(np.float32).reshape(1,-1); py=(c0[1]+r*n[1]).astype(np.float32).reshape(1,-1)
    # average along a 9 px stretch
    prof=np.mean([cv2.remap(Y,(px+k*d[0]).astype(np.float32),(py+k*d[1]).astype(np.float32),cv2.INTER_LINEAR)[0] for k in range(-4,5)],axis=0)
    g=np.gradient(prof)
    # print strongest edges
    idx=np.argsort(-np.abs(g))
    picks=[]
    for j in idx:
        if all(abs(j-q)>6 for q in picks): picks.append(j)
        if len(picks)==4: break
    picks=sorted(picks)
    print(f's={s:5d} c=({c0[0]:6.1f},{c0[1]:6.1f})', ' '.join(f'r={r[j]:6.1f}(g={g[j]:+.1f})' for j in picks))
