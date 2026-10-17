import numpy as np
T=np.loadtxt('/home/user/quantiphy-challenge/research/next/audit3/internet_02/remeasure/ball_track_full.txt')
fr=T[:,0]; x=T[:,1]-T[:,6]; y=T[:,2]-T[:,7]
D=dict(zip(fr.astype(int),zip(x,y)))
arcs={'A':range(50,60),'B':range(63,71),'C':range(72,81),'D':range(82,90),'E':range(92,100),'F':range(101,107),'G':range(111,115),'H':range(132,138)}
res={}
for k,r in arcs.items():
    t=np.array([i for i in r if i in D and not np.isnan(D[i][1])],float)
    yy=np.array([D[i][1] for i in t.astype(int)]); xx=np.array([D[i][0] for i in t.astype(int)])
    p=np.polyfit(t,yy,2); g=2*p[0]
    resid=yy-np.polyval(p,t)
    px=np.polyfit(t,xx,1)
    # leave-one-out-ish: also fit dropping endpoints
    p2=np.polyfit(t[1:-1],yy[1:-1],2) if len(t)>4 else p
    res[k]=(g,2*p2[0],px[0],np.abs(resid).max(),len(t))
    print(k,'n=%d g=%.2f g_inner=%.2f vx=%.2f maxres=%.2f'%(len(t),g,2*p2[0],px[0],np.abs(resid).max()))
gs=np.array([res[k][0] for k in 'ABCDE'])
print('mean g A-E %.2f median %.2f std %.2f'%(gs.mean(),np.median(gs),gs.std()))
# velocity at frame 75 (t=2.50 s, frame k at t=k/30)
s=9.8/900/19.5
for name,r in [('C 72-80',range(72,81)),('C 73-79',range(73,80)),('C 72-79',range(72,80)),('C 73-80',range(73,81))]:
    t=np.array([i for i in r],float); yy=np.array([D[i][1] for i in r]); xx=np.array([D[i][0] for i in r])
    p=np.polyfit(t,yy,2); px=np.polyfit(t,xx,2)
    vy=np.polyval(np.polyder(p),75); vx=np.polyval(np.polyder(px),75)
    # constrained: fix g=19.5
    A=np.vstack([np.ones_like(t),t-75]).T; b=yy-0.5*19.5*(t-75)**2; c0,vyc=np.linalg.lstsq(A,b,rcond=None)[0]
    vxl=np.polyfit(t,xx,1)[0]
    sp=np.hypot(vx,vy); spc=np.hypot(vxl,vyc)
    print(name,'free: vx %.2f vy %.2f |v| %.2f px/f -> %.3f m/s ; g-fixed: vy %.2f vx(lin) %.2f |v| %.2f -> %.3f m/s'%(vx,vy,sp,sp*30*s,vyc,vxl,spc,spc*30*s))
for a,b in [(74,75),(74,76),(75,76),(73,77)]:
    v=np.hypot(D[b][0]-D[a][0],D[b][1]-D[a][1])/(b-a); print('diff',a,b,'%.2f px/f -> %.3f m/s'%(v,v*30*s))
