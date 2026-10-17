import json, numpy as np
f=711.; cx=640.; cy=360.; R=0.035
B=json.load(open('ballfit.json'))['captured_0010s']
U=np.array([r['u'] for r in B]); V=np.array([r['v'] for r in B])
J=np.arange(len(U)); CAP=J+(J>=12)+(J>=36)
def ray(u,v):
    d=np.stack([(np.asarray(u)-cx)/f,(np.asarray(v)-cy)/f,np.ones_like(np.asarray(u,float))],-1)
    return d/np.linalg.norm(d,axis=-1,keepdims=True)
def uv_at_cap(c):
    return np.interp(c,CAP,U), np.interp(c,CAP,V)
anch_t=np.array([.3,.6,.9,1.2,1.5,1.8]); anch_d=np.array([1.706,1.344,1.4605,1.784,1.717,1.35])
