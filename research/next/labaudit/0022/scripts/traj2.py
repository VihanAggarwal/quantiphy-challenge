import numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
T=json.load(open(S+'track_diff.json'))
CX,CY=640.,360.; FPS=24.0
F=711.0
n=np.array(json.load(open(S+'plane_711.json'))['n'])
def ray(p): return np.array([(p[0]-CX)/F,(p[1]-CY)/F,1.])
def bp_range(p,R): r=ray(p); return R*r/np.linalg.norm(r)
def onplane(p,d): r=ray(p); return d/np.dot(n,r)*r
def interp(tr,fi):
    i=int(np.floor(fi)); a=fi-i
    return (1-a)*np.array(tr[i][:2])+a*np.array(tr[i+1][:2])
for rend in ['x','s']:
    tr=T[rend]
    for anchor,R in [(0.6,1.751),(0.8,1.687),(1.2,1.526)]:
        dball=n@bp_range(interp(tr,anchor*FPS),R)
        P=np.array([onplane(tr[i][:2],dball) for i in range(46)])
        # arc length along path
        steps=np.linalg.norm(np.diff(P,axis=0),axis=1)
        s=np.concatenate([[0],np.cumsum(steps)])*100  # cm
        t=np.arange(46)/FPS
        # fit quadratic s(t) on moving frames 13..44
        m=(np.arange(46)>=13)&(np.arange(46)<=44)
        # use displacement from start position rather than arc length (less noise)
        disp=np.linalg.norm(P-P[11],axis=1)*100
        c=np.polyfit(t[m],disp[m],2)
        v=lambda tt: 2*c[0]*tt+c[1]
        dispf=lambda tt: np.polyval(c,tt)
        # local linear fits (+-3 frames) for speed
        def vloc(tt,hw=3):
            fi=tt*FPS; idx=np.arange(int(round(fi))-hw,int(round(fi))+hw+1)
            return np.polyfit(t[idx],disp[idx],1)[0]
        P06=onplane(interp(tr,0.6*FPS),dball); P16=onplane(interp(tr,1.6*FPS),dball)
        print(f'{rend} anchor {anchor}: quad a={2*c[0]:.1f} cm/s2  v(0.8)={v(0.8):.1f} v(1.2)={v(1.2):.1f} | local v(0.8)={vloc(0.8):.1f} v(1.2)={vloc(1.2):.1f} | disp 0.6-1.6 direct {100*np.linalg.norm(P16-P06):.1f}, quad {dispf(1.6)-dispf(0.6):.1f}')
    # print per-frame disp for anchor 0.6
    dball=n@bp_range(interp(tr,0.6*FPS),1.751)
    P=np.array([onplane(tr[i][:2],dball) for i in range(46)])
    disp=np.linalg.norm(P-P[11],axis=1)*100
    print(rend,'disp per frame',np.round(disp,1).tolist())
    print(rend,'step per frame cm',np.round(np.diff(disp)[10:],2).tolist())
