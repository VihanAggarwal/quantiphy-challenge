import cv2, numpy as np, json
C=np.load('corners.npy')  # BL BR FR FL (image)
W,Dp=60.3,76.0
obj=np.array([[0,Dp],[W,Dp],[W,0],[0,0]],float)
Hm=cv2.getPerspectiveTransform(C.astype(np.float32),obj.astype(np.float32))
c=json.load(open('circ_captured_0031.json'))
fps=24.
def traj(pts,i,lo,hi,deg):
    sel=(i>=lo)&(i<=hi); t=i[sel]/fps
    out={}
    for tq in [36/fps,38/fps,1.6,40/fps]:
        v=[np.polyval(np.polyder(np.polyfit(t,pts[sel,k],deg)),tq) for k in range(pts.shape[1])]
        out[round(tq,3)]=np.linalg.norm(v)
    return out
i=np.array([r['i'] for r in c],float)
u=np.array([r['cx'] for r in c]); v=np.array([r['cy'] for r in c]); d=np.array([r['d'] for r in c])
# route 2b: homography on bottom point
bot=np.c_[u,v+d/2].astype(np.float32).reshape(-1,1,2)
T=cv2.perspectiveTransform(bot,Hm).reshape(-1,2)
for k in [0,14,30,34,36,38,40,42,44,48]: print('frame',k,'table xy (cm)',T[k].round(1))
for lo,hi in [(26,48),(30,48),(32,46)]:
    for deg in [2,3]:
        print('H-route win',lo,hi,'deg',deg,{k:round(x,1) for k,x in traj(T,i,lo,hi,deg).items()})
# route 2a: pose with K, ray-plane z=2
for f in [690,711,730]:
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    o3=np.c_[obj,np.zeros(4)]
    ok,rv,tv=cv2.solvePnP(o3,C,K,None,flags=cv2.SOLVEPNP_IPPE)
    Rm,_=cv2.Rodrigues(rv); cam=-Rm.T@tv.ravel()
    rays=(Rm.T@np.linalg.inv(K)@np.c_[u,v,np.ones_like(u)].T).T
    s=(2.0-cam[2])/rays[:,2]; P=cam+s[:,None]*rays
    for lo,hi in [(26,48),(30,48)]:
        for deg in [2,3]:
            print('pose f',f,'cam',cam.round(1),'win',lo,hi,'deg',deg,{k:round(x,1) for k,x in traj(P[:,:2],i,lo,hi,deg).items()})
    print('   frame 38 P',P[38].round(1),' range from cam',np.linalg.norm(P[38]-cam).round(1))
