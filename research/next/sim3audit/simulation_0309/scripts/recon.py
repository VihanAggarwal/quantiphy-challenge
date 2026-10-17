# 3D reconstruction of glide-phase tracks under the Z convention; along-V coordinates
import numpy as np, cv2
d=np.load('joint0302.npz'); T=d['T']; t=d['t']; vp=d['vp']; s=d['s']
c=np.array([1280.,720.])
w=vp-c
Vmag=1.29
for f in [3300,3450,3556,3579,3700]:
    Vh=np.array([w[0],w[1],f]); Vh/=np.linalg.norm(Vh)
    Vz=Vmag*Vh[2]
    # reference frame index 0 (frame 51)
    t0=t[0]
    Z=Vz*(t0-s)
    X=np.stack([Z*(T[0,:,0]-c[0])/f, Z*(T[0,:,1]-c[1])/f, Z],1)
    a=X@Vh
    print(f'f={f} Vz={Vz:.4f} along-V extent of tracked pts {a.max()-a.min():.3f} m; s-range*|V| {Vmag*(s.max()-s.min()):.3f}')
np.save('Vh.npy',Vh)
