# Kinematics with real-time base: original capture 25 fps, video 24 fps made by dropping frames.
# Observed drop: video frames 35->36 show a double step (3.5 cm vs ~1.7 cm). Second drop assumed at <=11 (ball at rest).
import numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
T=json.load(open(S+'track_diff.json'))
CX,CY=640.,360.; F=711.0
n=np.array(json.load(open(S+'plane_711.json'))['n'])
def ray(p): return np.array([(p[0]-CX)/F,(p[1]-CY)/F,1.])
def bp_range(p,R): r=ray(p); return R*r/np.linalg.norm(r)
def onplane(p,d): r=ray(p); return d/np.dot(n,r)*r
for rend in ['x','s','o']:
    tr=T[rend]
    vid=np.arange(46)
    for drop12 in [False,True]:
        orig=vid+(vid>=36)+((vid>=12) if drop12 else 0)
        t=orig/25.0
        # stated t -> video frame (nearest original frame)
        def vf(tt): return int(np.argmin(np.abs(t-tt)))
        i06=vf(0.6)
        dball=n@bp_range(tr[i06][:2],1.751)
        P=np.array([onplane(tr[i][:2],dball) for i in vid])*100
        disp=np.linalg.norm(P-P[11],axis=1)
        m=(vid>=16)&(vid<=44)
        c=np.polyfit(t[m],disp[m],2)
        def vloc(tt,hw=3):
            k=vf(tt); idx=np.arange(k-hw,k+hw+1); return np.polyfit(t[idx],disp[idx],1)[0]
        def fwd(tt):
            k=vf(tt); return np.linalg.norm(P[k+1]-P[k])/(t[k+1]-t[k])
        # range check
        rng={tt:np.linalg.norm(P[vf(tt)])/100 for tt in [0.6,0.8,1.2,1.6]}
        print(f'{rend} drop12={drop12}: frames 0.6/0.8/1.2/1.6 -> {[vf(x) for x in [0.6,0.8,1.2,1.6]]}; a_quad={2*c[0]:.1f}; '
              f'v_quad(0.8)={2*c[0]*0.8+c[1]:.1f} v_quad(1.2)={2*c[0]*1.2+c[1]:.1f}; v_loc(0.8)={vloc(0.8):.1f} v_loc(1.2)={vloc(1.2):.1f}; '
              f'fwd(0.8)={fwd(0.8):.1f} fwd(1.2)={fwd(1.2):.1f}; disp0.6-1.6={np.linalg.norm(P[vf(1.6)]-P[vf(0.6)]):.1f}; plane ranges {[round(v,3) for v in rng.values()]}')
# Route 1: stated depths only (3 label points), straight line fit and extrapolation to 1.6
tr=T['x']
pts={}
for tt,R,k in [(0.6,1.751,14),(0.8,1.687,19),(1.2,1.526,29)]:
    pts[tt]=bp_range(tr[k][:2],R)*100
print('stated-depth points (cm):',{k:np.round(v,1).tolist() for k,v in pts.items()})
print('|P0.8-P0.6|=%.2f  |P1.2-P0.8|=%.2f  |P1.2-P0.6|=%.2f'%(np.linalg.norm(pts[0.8]-pts[0.6]),np.linalg.norm(pts[1.2]-pts[0.8]),np.linalg.norm(pts[1.2]-pts[0.6])))
v1=np.linalg.norm(pts[0.8]-pts[0.6])/0.2; v2=np.linalg.norm(pts[1.2]-pts[0.8])/0.4
print('avg v 0.6-0.8 = %.1f, avg v 0.8-1.2 = %.1f, implied a = %.1f'%(v1,v2,(v2-v1)/0.3))
# end point at 1.6 on plane through the stated 1.2 point vs through 0.6 point
for anchor_t,R,k in [(0.6,1.751,14),(1.2,1.526,29)]:
    d=n@bp_range(tr[k][:2],R)
    P16=onplane(tr[38][:2],d)*100
    print('disp 0.6->1.6 with start=stated(0.6), end on plane anchored at %.1f: %.1f'%(anchor_t,np.linalg.norm(P16-pts[0.6])))
