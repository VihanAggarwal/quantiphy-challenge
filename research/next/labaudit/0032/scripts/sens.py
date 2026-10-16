# Sensitivity of route B white-ball speed at t=1.6 s (capture clock) to f, principal point and table-corner errors.
import numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
C0={k:np.array(v) for k,v in json.load(open(d+'corners.json')).items()}
T=json.load(open(d+'track_o.json'))
def cap(i): return (i+(i>=12)+(i>=36))/25.
def run(f,cy,C):
    K=np.array([[f,0,640],[0,f,cy],[0,0,1.]]); Ki=np.linalg.inv(K)
    h=lambda p: np.array([p[0],p[1],1.])
    def vp(a,b,c,e): return np.cross(np.cross(h(a),h(b)),np.cross(h(c),h(e)))
    v1=Ki@vp(C['BL'],C['FL'],C['BR'],C['FR']); v2=Ki@vp(C['BL'],C['BR'],C['FL'],C['FR'])
    nn=np.cross(v1/np.linalg.norm(v1),v2/np.linalg.norm(v2)); nn/=np.linalg.norm(nn)
    if nn[1]<0: nn=-nn
    ray=lambda p: (lambda r: r/np.linalg.norm(r))(Ki@h(p))
    tb=T['36']['yel']; u=ray((tb['cx'],tb['cy'])); H=nn@(1.183*u)+0.0335
    pw=T['36']['wht']; Rp=np.linalg.norm(ray((pw['cx'],pw['cy']))*(H-0.02)/(nn@ray((pw['cx'],pw['cy']))))
    U={k:ray(v)*H/(nn@ray(v)) for k,v in C.items()}
    W=(np.linalg.norm(U['BR']-U['BL'])+np.linalg.norm(U['FR']-U['FL']))/2; D=(np.linalg.norm(U['FL']-U['BL'])+np.linalg.norm(U['FR']-U['BR']))/2
    fr=list(range(36,45)); P=np.array([ray((T[str(i)]['wht']['cx'],T[str(i)]['wht']['cy']))*(H-0.02)/(nn@ray((T[str(i)]['wht']['cx'],T[str(i)]['wht']['cy']))) for i in fr])
    tt=np.array([cap(i) for i in fr]); sel=np.abs(tt-1.6)<=0.1
    v=np.linalg.norm(np.polyfit(tt[sel]-1.6,P[sel],1)[0])*100
    v2_=np.linalg.norm(np.polyfit(tt,P,1)[0])*100
    return H,Rp,W*100,D*100,v,v2_
print('f cy dcorner | h  R_ping(stated 1.353)  W  D | v(1.6,±0.1) v(f36-44)')
for f in [690,711,730]:
    for cy in [350,360,370]:
        for dc in [0,-1.5,1.5]:
            C={k:v.copy() for k,v in C0.items()}
            C['FL'][0]+=dc; C['FR'][0]-=dc   # widen/narrow front edge -> moves the side-line vanishing point
            H,Rp,W,D,v,v2=run(f,cy,C)
            print(f,cy,dc,'| %.3f %.3f %.1f %.1f | %.1f %.1f'%(H,Rp,W,D,v,v2))
