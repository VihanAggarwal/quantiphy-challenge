import numpy as np, json
from geo import *
from lm import lsq
G=9.8
def frame_from_g(gd):
    e3=gd/np.linalg.norm(gd)
    a=np.array([1.,0,0]); e1=a-(a@e3)*e3; e1/=np.linalg.norm(e1); e2=np.cross(e3,e1)
    return e1,e2,e3
def unpack(p):
    sp,pu,pv,L,ga,gb,th,ph,va,vb,gam,dt0=p
    gd=np.array([np.sin(ga)*np.cos(gb),np.cos(ga),np.sin(ga)*np.sin(gb)])  # ga: angle from image-down axis
    return sp,pu,pv,L,gd,th,ph,va,vb,gam,dt0
def simulate(p,times,Rb=R):
    sp,pu,pv,L,gd,th,ph,va,vb,gam,dt0=unpack(p)
    P=sp*ray(pu,pv)
    e1,e2,e3=frame_from_g(gd)
    n=np.sin(th)*np.cos(ph)*e1+np.sin(th)*np.sin(ph)*e2+np.cos(th)*e3
    eth=np.cos(th)*np.cos(ph)*e1+np.cos(th)*np.sin(ph)*e2-np.sin(th)*e3
    eph=-np.sin(ph)*e1+np.cos(ph)*e2
    x=P+L*n; v=va*eth+vb*eph
    geff=G*L**2/(L**2+0.4*Rb**2)
    gv=geff*e3
    def acc(x,v):
        nn=(x-P)/L
        return gv-(gv@nn)*nn-(v@v)/L*nn-gam*v
    h=1/1000.; t=0.0; out=[]; times=np.asarray(times); order=np.argsort(times); res=np.zeros((len(times),3)); vel=np.zeros((len(times),3))
    k=0; ts=times[order]
    while k<len(ts):
        while k<len(ts) and ts[k]<=t+1e-12:
            res[order[k]]=x; vel[order[k]]=v; k+=1
        if k>=len(ts): break
        hh=min(h,ts[k]-t) if ts[k]-t>1e-12 else h
        k1v=acc(x,v); k1x=v
        k2v=acc(x+hh/2*k1x,v+hh/2*k1v); k2x=v+hh/2*k1v
        k3v=acc(x+hh/2*k2x,v+hh/2*k2v); k3x=v+hh/2*k2v
        k4v=acc(x+hh*k3x,v+hh*k3v); k4x=v+hh*k3v
        x=x+hh/6*(k1x+2*k2x+2*k3x+k4x); v=v+hh/6*(k1v+2*k2v+2*k3v+k4v)
        nn=(x-P); nn/=np.linalg.norm(nn); x=P+L*nn; v=v-(v@nn)*nn
        t+=hh
    return res,vel
def project(X):
    return cx+f*X[:,0]/X[:,2], cy+f*X[:,1]/X[:,2]
