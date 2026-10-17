import json, numpy as np
from math import *
base='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0110/'
def load(v):
    d=json.load(open(base+f'track_{v}.json'))
    L=np.array([[o['cx'],o['cy'],o['w'],o['h'],o['bbcx'],o['bbcy']] for r in d for o in r['objs'][:1]])
    R=np.array([[o['cx'],o['cy'],o['w'],o['h'],o['bbcx'],o['bbcy']] for r in d for o in r['objs'][1:2]])
    return L,R
def ray(u,v,f,W,H):
    r=np.array([(u-W/2)/f,(v-H/2)/f,1.0]); return r/np.linalg.norm(r)
def smooth(arr,i,k=3):
    # local linear fit around frame i
    idx=np.arange(max(0,i-k),min(len(arr),i+k+1))
    p=np.polyfit(idx,arr[idx],2); return np.polyval(p,i)
for v,W,H,r1,r2 in [('simulation_0109',1080,1080,22.0155,24.0333),('simulation_0110',1920,1080,17.9557,22.7150)]:
    L,R=load(v)
    for col,name in [(0,'centroid'),(4,'bbox')]:
        u1,v1=smooth(L[:,col],24),smooth(L[:,col+1],24)
        u2,v2=smooth(L[:,col],48),smooth(L[:,col+1],48)
        best=None
        for f in np.arange(800,6000,0.5):
            d=np.linalg.norm(r2*ray(u2,v2,f,W,H)-r1*ray(u1,v1,f,W,H))
            if best is None or abs(d-4.7833)<best[1]: best=(f,abs(d-4.7833))
        f=best[0]
        fb=50/36*W
        d_b=np.linalg.norm(r2*ray(u2,v2,fb,W,H)-r1*ray(u1,v1,fb,W,H))
        print(v,name,'f_triangle=%.1f'%f,'hfov=%.2f'%(2*degrees(atan(W/2/f))),' blender50mm f=%.1f -> |dP|=%.4f (prior 4.7833, %.2f%%)'%(fb,d_b,100*(d_b/4.7833-1)))
