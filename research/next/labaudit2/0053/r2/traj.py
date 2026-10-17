import numpy as np, json
f=711.;cx=640.;cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
T=json.load(open('bintrack.json'))
# video->capture mapping: drops after video 11 and after video 35
def cap(i): return i + (1 if i>=12 else 0) + (1 if i>=36 else 0)
R=np.array([ray(t['cx'],t['cy']) for t in T]); A=np.array([t['area'] for t in T])
cosa=R[:,2]
P10=2.73*R[10]
def nvec(p,r):
    p,r=np.radians(p),np.radians(r); return np.array([np.sin(r)*np.cos(p),-np.cos(r)*np.cos(p),-np.sin(p)])
models={}
for name,n in [('depthfit p37.4 r1.4',nvec(37.4,1.4)),('depthfit p36.3 r1.1',nvec(36.3,1.1)),('depthfit p39.1 r3.3',nvec(39.1,3.3)),('vertVP',np.load('normals.npy')[1]),('horizon',np.load('normals.npy')[0])]:
    s=(n@P10)/(R@n); models['plane '+name]=s[:,None]*R
for delta in [0.0,0.12]:
    om=A*cosa**3
    rc=(2.73+delta)*np.sqrt(om[10]/om)
    models[f'area d={delta}']=(rc-delta)[:,None]*R
caps=np.array([cap(i) for i in range(len(T))])
for name,P in models.items():
    # displacement capture 10 -> 35 : video 10 -> 34
    i10=10; i35=list(caps).index(35)
    d=np.linalg.norm(P[i35]-P[i10])
    # speed around capture 10: fit per-capture-frame velocity via linear fit over capture 7..13 window
    sel=(caps>=6)&(caps<=14)
    tt=caps[sel]/25.
    v=[np.polyfit(tt,P[sel,k],1)[0] for k in range(3)]
    fd=np.linalg.norm(P[11]-P[10])*25
    print(f'{name:24s} range34 {np.linalg.norm(P[i35]):.3f} disp(10->35) {d:.3f}  fit speed@0.4 {np.linalg.norm(v):.3f}  fwd diff 10->11 {fd:.3f}')
np.save('models.npy',{k:v for k,v in models.items()},allow_pickle=True)
