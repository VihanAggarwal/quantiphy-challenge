import json, numpy as np
def brentq(g,a,b):
    fa=g(a)
    for _ in range(200):
        c=(a+b)/2; fc=g(c)
        if (fc>0)==(fa>0): a,fa=c,fc
        else: b=c
    return (a+b)/2
r=json.load(open('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0017/rm1657/track2.json'))
fps=33.0
t=np.array([o['i'] for o in r])/fps
hx=np.array([o['head_x'] for o in r]); tx=np.array([o['torso_x'] for o in r]); top=np.array([o['top'] for o in r])
ok=(t>=4/fps)&(top<380)
for name,u in (('head',hx),('torso',tx)):
    m=ok&np.isfinite(u)
    p=np.polyfit(t[m],u[m],1); res=u[m]-np.polyval(p,t[m])
    print(name,'linear fit slope px/s %.2f  u(0)=%.1f u(1)=%.1f rms %.2f'%(p[0],np.polyval(p,0),np.polyval(p,1),res.std()))
    # projective fit
# solve f and Z from D0,D1 with u from head-lag pelvis offsets
D0,D1=5.424,4.886
m=ok&np.isfinite(hx)
p=np.polyfit(t[m],hx[m],1)
for lag in (0,8,12,16):
    u0=np.polyval(p,0)-lag-540; u1=np.polyval(p,1)-lag-540
    # pelvis vertical: assume ~ at horizon (y offset small); allow dy = 0
    def g(f):
        Z0=D0/np.sqrt(1+(u0/f)**2); Z1=D1/np.sqrt(1+(u1/f)**2)
        return Z0-Z1
    f=brentq(g,300,5000)
    Z=D0/np.sqrt(1+(u0/f)**2)
    sp=p[0]*Z/f
    # speed route: f/Z = slope/1.3 and D0 -> Z
    k=p[0]/1.3  # f/Z
    # D0 = Z*sqrt(1+(u0/f)^2) = sqrt(Z^2 + (u0/k)^2)
    Zs0=np.sqrt(D0**2-(u0/k)**2); fs0=k*Zs0
    Zs1=np.sqrt(D1**2-(u1/k)**2); fs1=k*Zs1
    print('lag %2d: ratio route f=%.1f Z=%.3f implied speed %.3f | speed route f=%.1f (D0) %.1f (D1), Z %.3f %.3f'%(lag,f,Z,sp,fs0,fs1,Zs0,Zs1))
