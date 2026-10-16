import sys, json; sys.path.insert(0,'.')
from recon import *
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
trx=json.load(open(f'{S}/tr_bx.json')); trs=json.load(open(f'{S}/tr_bs.json'))
def get(src,key,k):
    if src=='hull': d=trx['bbfull'][str(k)]; return d['cx'],d['cy'],d['hull_minor']
    if src=='full': d=trx['bbfull'][str(k)]; return d['cx'],d['cy'],d['minor']
    if src=='orange': d=trx['bb'][str(k)]; return d['cx'],d['cy'],d['minor']
    if src=='bsmin': d=trs['bb'][str(k)]; return d['cx'],d['cy'],d['minor']
    if src=='bsdeq': d=trs['bb'][str(k)]; return d['cx'],d['cy'],np.sqrt(4*d['A']/np.pi)
def rng(src,t):
    x=t*24; i0=int(np.floor(x)); a=x-i0
    u0,v0,d0=get(src,'bb',i0); u1,v1,d1=get(src,'bb',i0+1)
    u,v,d=(1-a)*u0+a*u1,(1-a)*v0+a*v1,(1-a)*d0+a*d1
    r=ray(u,v); cosa=r[2]
    return 165.0/(d*cosa),(u,v)
P1=2.7777*ray(*rng('hull',0.9)[1])
for src in ['hull','full','orange','bsmin','bsdeq']:
    ks=[]
    for t,st in [(0.9,2.7777),(1.4,2.602)]:
        r,_=rng(src,t); ks.append(st/r)
    k=np.mean(ks)
    rests=[]
    for kk in [5,6,7,8,9]:
        u,v,d=get(src,'bb',kk); r=ray(u,v); rests.append(165.0/(d*r[2]))
    r0=np.median(rests)*k
    P0=r0*ray(828.4,280.0)
    print('%-6s k=%.3f (%.3f,%.3f) rest range raw %.3f calibrated %.3f  disp(rest->0.9s) %.1f cm'%(src,k,ks[0],ks[1],np.median(rests),r0,100*np.linalg.norm(P1-P0)))
