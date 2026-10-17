import numpy as np
f=711.; fps=25.; g=9.8
t=np.array([28,29,30,31,32,33,34,35,37,38,39],float)
bot=np.array([291,295,305,322,337,361,387,418,491,531,576],float)
top=np.array([236,238,245,260,270,290,316,345,410,450,494],float)
mid=(bot+top)/2
def sim(Z,vt,y0,v0,t0,tt):
    # integrate pixel motion: a_px = (f g/Z)(1-(v_m/vt)^2), v_m = v_px*fps*Z/f
    dt=0.01; T=np.arange(t0,tt.max()+1e-9,dt); y=y0; v=v0; out={}
    ys=[];
    for k,tk in enumerate(T):
        ys.append(y)
        vm=v*fps*Z/f
        a=(f*g/Z)/fps**2*(1-np.sign(vm)*(vm/vt)**2 if vt<1e8 else 1)
        y+=v*dt+0.5*a*dt*dt; v+=a*dt
    ys=np.array(ys); return np.interp(tt,T,ys)
for lab,y in [('mid',mid),('bot',bot),('top',top)]:
  for lo in [29,30,31]:
    sel=t>=lo; tt=t[sel]; yy=y[sel]
    best=[]
    for Z in np.arange(2.3,3.6,0.02):
      for vt in [4,5,6,7,8,10,13,20,1e9]:
        # fit y0,v0 at t0=lo by small grid via linearization: do coarse search
        bb=None
        for v0 in np.arange(0,30,0.5):
            p=sim(Z,vt,0.0,v0,lo,tt); y0=np.mean(yy-p); e=np.sqrt(np.mean((p+y0-yy)**2))
            if bb is None or e<bb[0]: bb=(e,v0)
        best.append((bb[0],Z,vt,bb[1]))
    best.sort()
    print(lab,'from c%d'%lo,'best:',[('rms %.2f Z %.2f vt %s v0 %.1f'%(e,Z,('inf' if vt>1e8 else vt),v0)) for e,Z,vt,v0 in best[:5]])
    # profile: best rms per vt
    for vt in [5,6,7,8,10,13,1e9]:
        b=min([r for r in best if r[2]==vt]); print('    vt=%s: Z=%.2f rms %.2f'%('inf' if vt>1e8 else vt,b[1],b[0]))
