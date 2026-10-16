# Capture-clock (25 fps, frames dropped after video frames 11/35) speeds of both balls, route B (table plane) and
# route A (stated range at f36 scaled by apparent width), from the x and o tracks.
import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0032/scripts')
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
G=np.load(d+'plane711.npy',allow_pickle=True).item(); n=-G['n']
f=711.; Ki=np.linalg.inv(np.array([[f,0,640],[0,f,360],[0,0,1.]]))
def ray(p): r=Ki@np.array([p[0],p[1],1.]); return r/np.linalg.norm(r)
def cap(i): return (i+(i>=12)+(i>=36))/25.
from route_a import width
H=0.173
res={}
for r in ['x','o']:
    T=json.load(open(d+'track_%s.json'%r))
    for name,key,R36,rad,chan,fr in [('ping','wht',1.353,0.02,'g',range(33,49)),('tennis','yel',1.183,0.0335,'s',range(30,42))]:
        fr=[i for i in fr if T[str(i)][key] is not None]
        uv={i:(T[str(i)][key]['cx'],T[str(i)][key]['cy']) for i in fr}
        XB={i:ray(uv[i])*(H-rad)/(n@ray(uv[i])) for i in fr}
        W={i:width(r,i,uv[i][0],uv[i][1],chan) for i in fr}
        XA={i:R36*W[36]/W[i]*ray(uv[i]) for i in fr}
        tt=np.array([cap(i) for i in fr])
        for lab,X in [('B',XB),('A',XA)]:
            P=np.array([X[i] for i in fr])
            fwd=[(fr[k],100*np.linalg.norm(P[k+1]-P[k])/(tt[k+1]-tt[k])) for k in range(len(fr)-1)]
            out=[]
            for t0 in [1.5,1.52,1.6]:
                for half in [0.08,0.12]:
                    sel=np.abs(tt-t0)<=half+1e-9
                    if sel.sum()<3: continue
                    c=np.polyfit(tt[sel]-t0,P[sel],1)
                    out.append('t%.2f±%.2f lin %.1f'%(t0,half,100*np.linalg.norm(c[0])))
            print(r,name,lab,' fwd:',' '.join('%d:%.0f'%a for a in fwd))
            print('      ',' | '.join(out))
            res[(r,name,lab)]=dict(fr=fr,P=P.tolist(),t=tt.tolist())
    # distance at f36
    for lab in ['B','A']:
        a=np.array(res[(r,'tennis',lab)]['P'])[res[(r,'tennis',lab)]['fr'].index(36)]
        b=np.array(res[(r,'ping',lab)]['P'])[res[(r,'ping',lab)]['fr'].index(36)]
        print(r,lab,'distance f36 %.2f cm'%(100*np.linalg.norm(a-b)))
import pickle; pickle.dump(res,open(d+'capclock.pkl','wb'))
