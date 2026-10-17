import numpy as np, json
exec(open('fit3d.py').read().split("for name,imax in")[0])
import cv2
fs=frames('ax')
# lowest extent of ball blob in bounce frame: for each row the alpha-weighted, find bottom-most rows; estimate bottom edge then center = bottom - D/2
def alpha_img(f):
    b,g,r=[f[:,:,k].astype(float) for k in range(3)]
    return np.clip(1-((g-(r+b)/2)-20)/(252-20),0,1)
for name,imax,ib,(u0,v0) in (('white',37,38,(358,669)),('green',36,37,(340,657))):
    A=alpha_img(fs[ib]); sub=A[v0-40:v0+40,u0-30:u0+30]
    rows=sub.sum(1)
    nz=np.nonzero(rows>2)[0]
    print(name,'bounce frame v%d rows with alpha: top y=%d bottom y=%d'%(ib,v0-40+nz[0],v0-40+nz[-1]))
    for ua in (True,False):
        s,I,J,uv,P=fit(name,imax,ua)
        ts=np.linspace(0.4,0.7,3001)
        PP=traj(s.x,ts); pr=proj(PP)
        for vb in (v0-40+nz[-1]-9, v0-40+nz[-1]-11):
            k=np.argmin(abs(pr[:,1]-vb))
            print('   %s fit: traj reaches image y=%d at c%.2f, pixel x=%.1f, h_below_cam=%.3f -> H_cam=%.3f, range=%.3f'%('anchor' if ua else 'free',vb,25+ts[k]*25,pr[k,0],PP[k]@down,PP[k]@down+rad[name],np.linalg.norm(PP[k])))
