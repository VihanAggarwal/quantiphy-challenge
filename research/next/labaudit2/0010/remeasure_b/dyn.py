import numpy as np
from geo import *
G=9.8
H=0.002; TMAX=2.1
def setup(p):
    p=np.atleast_2d(p)
    sp,pu,pv,L,ga,gb,th,ph,va,vb,gam=[p[:,k] for k in range(11)]
    gd=np.stack([np.sin(ga)*np.cos(gb),np.cos(ga),np.sin(ga)*np.sin(gb)],-1)
    e3=gd
    a=np.array([1.,0,0])[None]
    e1=a-(np.sum(a*e3,-1,keepdims=True))*e3; e1/=np.linalg.norm(e1,axis=-1,keepdims=True); e2=np.cross(e3,e1)
    n=(np.sin(th)*np.cos(ph))[:,None]*e1+(np.sin(th)*np.sin(ph))[:,None]*e2+np.cos(th)[:,None]*e3
    eth=(np.cos(th)*np.cos(ph))[:,None]*e1+(np.cos(th)*np.sin(ph))[:,None]*e2-np.sin(th)[:,None]*e3
    eph=-np.sin(ph)[:,None]*e1+np.cos(ph)[:,None]*e2
    P=sp[:,None]*ray(pu,pv)
    x=P+L[:,None]*n; v=va[:,None]*eth+vb[:,None]*eph
    geff=G*L**2/(L**2+0.4*R**2)
    gv=geff[:,None]*e3
    return P,L,x,v,gv,gam
def simulate(p):
    """returns grid times, X[B,T,3], Vel[B,T,3]"""
    P,L,x,v,gv,gam=setup(p)
    Lc=L[:,None]
    def acc(x,v):
        nn=(x-P)/Lc
        return gv-np.sum(gv*nn,-1,keepdims=True)*nn-np.sum(v*v,-1,keepdims=True)/Lc*nn-gam[:,None]*v
    nT=int(round(TMAX/H))+1
    X=np.empty((len(L),nT,3)); Vv=np.empty_like(X)
    for i in range(nT):
        X[:,i]=x; Vv[:,i]=v
        k1v=acc(x,v); k1x=v
        k2v=acc(x+H/2*k1x,v+H/2*k1v); k2x=v+H/2*k1v
        k3v=acc(x+H/2*k2x,v+H/2*k2v); k3x=v+H/2*k2v
        k4v=acc(x+H*k3x,v+H*k3v); k4x=v+H*k3v
        x=x+H/6*(k1x+2*k2x+2*k3x+k4x); v=v+H/6*(k1v+2*k2v+2*k3v+k4v)
        nn=x-P; nn/=np.linalg.norm(nn,axis=-1,keepdims=True); x=P+Lc*nn; v=v-np.sum(v*nn,-1,keepdims=True)*nn
    return np.arange(nT)*H,X,Vv
def sample(tg,X,Vv,t):
    """cubic Hermite sample at times t (array)"""
    t=np.asarray(t,float); i=np.clip((t/H).astype(int),0,len(tg)-2); s=((t-tg[i])/H)[None,:,None]
    x0=X[:,i];x1=X[:,i+1];v0=Vv[:,i]*H;v1=Vv[:,i+1]*H
    h00=2*s**3-3*s**2+1;h10=s**3-2*s**2+s;h01=-2*s**3+3*s**2;h11=s**3-s**2
    return h00*x0+h10*v0+h01*x1+h11*v1
def project(X):
    return cx+f*X[...,0]/X[...,2], cy+f*X[...,1]/X[...,2]
