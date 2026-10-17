import numpy as np, sys
s=0.438/float(sys.argv[2]) if len(sys.argv)>2 else 0.438/120.4
t=np.loadtxt(sys.argv[1],delimiter=',')
p=t[:,1:3]
fps=24
v=np.r_[np.nan,np.hypot(*np.diff(p,axis=0).T)]*fps*s
def local(n0, half, deg):
    idx=np.arange(n0-half,n0+half+1)
    # positions polyfit, evaluate velocity analytic and discrete second differences
    cx=np.polyfit(idx-n0,p[idx,0],deg); cy=np.polyfit(idx-n0,p[idx,1],deg)
    dcx=np.polyder(cx); dcy=np.polyder(cy); ddcx=np.polyder(dcx); ddcy=np.polyder(dcy)
    vx,vy=np.polyval(dcx,0),np.polyval(dcy,0); ax,ay=np.polyval(ddcx,0),np.polyval(ddcy,0)
    sp=np.hypot(vx,vy); a_an=(vx*ax+vy*ay)/sp  # d|v|/dt at n0 (px/frame^2)
    # discrete: backward speeds from smooth positions
    P=lambda k: np.array([np.polyval(cx,k),np.polyval(cy,k)])
    vb=lambda k: np.linalg.norm(P(k)-P(k-1))
    a_bb=vb(0)-vb(-1)   # (v_n - v_{n-1})
    a_fb=vb(1)-vb(0)    # (v_{n+1}-v_n)
    a_c=(vb(1)-vb(-1))/2
    k=s*fps*fps
    return sp*s*fps, a_an*k, a_bb*k, a_fb*k, a_c*k
# speed-series local fit
def local_v(n0, half, deg):
    idx=np.arange(n0-half,n0+half+1)
    # v_n represents speed at n-0.5
    c=np.polyfit(idx-0.5-n0,v[idx],deg)
    return np.polyval(c,0), np.polyval(np.polyder(c),0)*fps, np.polyval(np.polyder(c),-0.5)*fps, np.polyval(np.polyder(c),-1)*fps
print('raw v around 24:',' '.join('%d:%.3f'%(i,v[i]) for i in range(18,32)))
print('raw v around 48:',' '.join('%d:%.3f'%(i,v[i]) for i in range(42,56)))
for n0 in [24,48]:
    print('== frame',n0)
    for half in [4,5,6,8,10]:
        for deg in [2,3,4]:
            if 2*half+1<=deg+2: continue
            r=local(n0,half,deg)
            print(' pos half %2d deg %d: speed %.3f  a_analytic %.3f  a_backbk %.3f a_fwd %.3f a_central %.3f'%((half,deg)+r))
    for half in [4,5,6,8]:
        for deg in [1,2,3]:
            r=local_v(n0,half,deg)
            print(' vser half %2d deg %d: v(t) %.3f  dv/dt@t %.3f  @t-0.5f %.3f @t-1f %.3f'%((half,deg)+r))
