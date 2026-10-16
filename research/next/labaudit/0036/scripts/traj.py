import numpy as np, json
f=711.; cx,cy=640.,360.
n=np.load('scripts/plane_n.npy')
T=json.load(open('scripts/trk_o.json'))
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
# stated points: interpolate pixel at video frame 21.5 and 34
def pix(kf):
    k0=int(np.floor(kf)); a=kf-k0
    p0=np.array([T[str(k0)]['cx'],T[str(k0)]['cy']]); 
    if a==0: return p0
    p1=np.array([T[str(k0+1)]['cx'],T[str(k0+1)]['cy']]); return (1-a)*p0+a*p1
for (k1,k2,lab) in [(21.5,34,'25fps-drop map'),(21.6,33.6,'24fps'),(21,34,'nearest a'),(22,34,'nearest b'),(22,35,'c')]:
    for dr in [0.0,0.02]:
        P1=ray(*pix(k1))*(1.01+dr); P2=ray(*pix(k2))*(0.716+dr)
        print(lab,k1,k2,'dr',dr,'disp %.1f cm'%(100*np.linalg.norm(P2-P1)),' plane heights %.4f %.4f'%(n@P1,n@P2))
