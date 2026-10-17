import json, numpy as np
# parabola fits of the image track on the 25 fps capture clock (drops after video frames 11 and 35)
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0028/track.json'))
def cap(k): return k + (k>=12) + (k>=36)
for V in ['captured_0028x','captured_0028']:
    tr=T[V]; k=np.arange(49); n=np.array([cap(i) for i in k]); x=np.array([r['cx'] for r in tr]); y=np.array([r['cy'] for r in tr])
    print(V)
    # step sizes (px per capture step) to show the dropped frame
    for i in range(30,40): print(f'  video {i}->{i+1}: dy={y[i+1]-y[i]:6.1f}  capture step={n[i+1]-n[i]}')
    segs={'fall':range(21,26),'arc1':range(28,36),'arc2':range(38,47)}
    P={}
    for s,rg in segs.items():
        rg=list(rg); c=np.polyfit(n[rg],y[rg],2); cxl=np.polyfit(n[rg],x[rg],1)
        res=y[rg]-np.polyval(c,n[rg])
        P[s]=c
        print(f'  {s}: video {rg[0]}-{rg[-1]} y accel={2*c[0]:.2f} px/capframe^2  vertex n={-c[1]/(2*c[0]):.2f} y={np.polyval(c,-c[1]/(2*c[0])):.1f}  x-vel={cxl[0]:.2f} px/fr  rms={res.std():.2f}')
    # contact times: where fall / arc1 parabolas intersect; arc1 / arc2
    for a,b in [('fall','arc1'),('arc1','arc2')]:
        d=P[a]-P[b]; r=np.roots(d); r=r[np.isreal(r)].real
        print(f'  {a}/{b} intersections n={np.round(r,2)} y={[round(np.polyval(P[a],q),1) for q in r]}')
