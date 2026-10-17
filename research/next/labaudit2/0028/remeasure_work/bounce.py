import numpy as np, json
W='research/next/labaudit2/0028/remeasure_work'
tr=json.load(open(f'{W}/track_captured_0028x.json'))
def cap(k): return k + (k>=12) + (k>=36)
def pfit(frames,deg=2):
    t=np.array([cap(k) for k in frames],float)
    y=np.array([tr[k]['cy'] for k in frames]); x=np.array([tr[k]['cx'] for k in frames])
    py=np.polyfit(t,y,deg); px=np.polyfit(t,x,1)
    res=y-np.polyval(py,t)
    return py,px,np.sqrt(np.mean(res**2))
arcs={'a1':list(range(22,26)),'a2':list(range(27,36)),'a3':list(range(37,46))}
P={k:pfit(v) for k,v in arcs.items()}
for k,(py,px,r) in P.items():
    tap=-py[1]/(2*py[0]); print(k,'accel px/capframe^2 %.3f'%(2*py[0]),'apex t(cap) %.2f'%tap,'apex y %.2f'%np.polyval(py,tap),'x slope %.3f'%px[0],'rms %.2f'%r)
def inter(a,b,lo,hi):
    d=P[a][0]-P[b][0]; rts=np.roots(d); rts=[r.real for r in rts if abs(r.imag)<1e-9 and lo<=r.real<=hi]
    return rts
for a,b,lo,hi in [('a1','a2',25,29),('a2','a3',35,40)]:
    for t in inter(a,b,lo,hi):
        y=np.polyval(P[a][0],t); x=np.polyval(P[a][1],t); x2=np.polyval(P[b][1],t)
        print(a,b,'bounce t_cap %.2f y_c %.2f x %.2f/%.2f'%(t,y,x,x2))
