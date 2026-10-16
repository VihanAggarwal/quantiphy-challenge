import numpy as np, cv2
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
F=711.0; CX=640.0; CY=360.0
def load(r):
    return np.load(S+f'fr0018{r}.npy')
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d
def bp_range(u,v,rng,f=F):
    d=ray(u,v,f); return rng*d/np.linalg.norm(d)
def bp_z(u,v,z,f=F):
    return z*ray(u,v,f)
def zfromrange(u,v,rng,f=F):
    return rng/np.linalg.norm(ray(u,v,f))
def fgmask(img,thr=40):
    return np.abs(img.astype(int)-255).max(2)>thr
