import numpy as np
exec(open('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0110/scripts/geom.py').read().split('for v,W,H')[0])
for v,W,H,f,r1,r2 in [('simulation_0109',1080,1080,1500.0,22.0155,24.0333),('simulation_0110',1920,1080,2666.67,17.9557,22.7150)]:
    L,R=load(v)
    for col in (0,4):
        uL,vL=smooth(L[:,col],24),smooth(L[:,col+1],24)
        uR,vR=smooth(R[:,col],24),smooth(R[:,col+1],24)
        PL=r1*ray(uL,vL,f,W,H)
        # right range: (a) equal size -> range ratio = width ratio (approx, use mean of w,h)
        sL=(smooth(L[:,2],24)+smooth(L[:,3],24))/2; sR=(smooth(R[:,2],24)+smooth(R[:,3],24))/2
        rR_a=r1*sL/sR
        # (b) same 3D velocity: right range from t=1 such that the right track matches left velocity -> use range ratio of left applied
        PR_a=rR_a*ray(uR,vR,f,W,H)
        # (b) same velocity: find rR such that P_R(t2)-P_R(t1) = vel_L, solve least squares over rR1,rR2
        uL2,vL2=smooth(L[:,col],48),smooth(L[:,col+1],48); uR2,vR2=smooth(R[:,col],48),smooth(R[:,col+1],48)
        velL=r2*ray(uL2,vL2,f,W,H)-PL
        A=np.stack([-ray(uR,vR,f,W,H), ray(uR2,vR2,f,W,H)],1)
        sol,*_=np.linalg.lstsq(A,velL,rcond=None)
        PR_b=sol[0]*ray(uR,vR,f,W,H)
        print(v,'col',col,'sizeRatio rR=%.3f sep=%.3f | sameVel rR=%.3f sep=%.3f'%(rR_a,np.linalg.norm(PR_a-PL),sol[0],np.linalg.norm(PR_b-PL)))
