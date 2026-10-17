import numpy as np
from math import *
exec(open('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0110/scripts/geom.py').read().split('for v,W,H')[0])
out={}
for v,W,H,f,r1,r2 in [('simulation_0109',1080,1080,1500.0,22.0155,24.0333),('simulation_0110',1920,1080,2666.67,17.9557,22.7150)]:
    L,R=load(v)
    u1,v1=smooth(L[:,4],24),smooth(L[:,5],24); u2,v2=smooth(L[:,4],48),smooth(L[:,5],48)
    P1=r1*ray(u1,v1,f,W,H); P2=r2*ray(u2,v2,f,W,H); vel=P2-P1
    print(v,'P1',P1.round(3),'P2',P2.round(3),'v',vel.round(3),'|v|=%.4f'%np.linalg.norm(vel))
    out[v]=(P1,P2,vel)
    if v=='simulation_0109':
        z=np.array([0,0,1.0])
        a=degrees(acos(abs(vel@z)/np.linalg.norm(vel)))
        los=(P1+P2)/2; los/=np.linalg.norm(los)
        a2=degrees(acos(abs(vel@los)/np.linalg.norm(vel)))
        print(' angle(v, optical axis)=%.2f deg ; angle(v, mid line of sight)=%.2f deg'%(a,a2))
        alpha=a
# 0110: n in plane spanned by line of sight to cell (at t=1) and image vertical; param by tilt angle th from line of sight toward image up
P1,P2,vel=out['simulation_0110']
vh=vel/np.linalg.norm(vel)
for tframe,P in [('t=1',P1),('t=2',P2)]:
    los=P/np.linalg.norm(P)
    up=np.array([0,-1.0,0]); up=up-(up@los)*los; up/=np.linalg.norm(up)
    print(tframe,'angle(v,los)=%.2f'%degrees(acos(vh@los)))
    for th in np.arange(50,80.1,2):
        # axis n pointing 'up' from the disk toward camera side: n = cos(th)*(-los) + sin(th)*up
        n=cos(radians(th))*(-los)+sin(radians(th))*up
        print('  th=%.0f angle(v,n)=%.2f'%(th,degrees(acos(abs(vh@n)))))
