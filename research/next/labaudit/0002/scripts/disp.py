import numpy as np
tr={int(r[0]):r[1:] for r in np.load('scripts/track_board.npy')}
def P(p,d,f=711.):
    v=np.array([(p[0]-640)/f,(p[1]-360)/f,1.]); return d*v/np.linalg.norm(v)
p0=tr[24]
for k in [31,32]:
    for f in [700,711,730]:
        print('t=1.3 as frame',k,'f',f,'disp %.2f cm'%(100*np.linalg.norm(P(p0,1.779,f)-P(tr[k],1.736,f))))
# interpolate frame for 31.2
p=tr[31]+(tr[32]-tr[31])*0.2
print('frame 31.2 disp %.2f'%(100*np.linalg.norm(P(p0,1.779)-P(p,1.736))))
# slope-plane consistent route: range along the slope interpolated from stated ends (offset so the t=1.0 ball gets 1.779)
def rng(y): return 1.815-(y-294)/126*0.1435-(1.815-(1.779+(282.7-294)/126*0.1435))
for k in range(24,36):
    print(k,'y %.1f'%tr[k][1],'plane-interp range %.3f'%rng(tr[k][1]),'disp from t1.0 %.2f cm'%(100*np.linalg.norm(P(p0,1.779)-P(tr[k],rng(tr[k][1])))))
