import numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
f=711.
def ray(x,y): return np.array([(x-640)/f,(y-360)/f,1.0])
# Route A plane (VP -59.8), anchor near
vp=(601.9,-59.8); dup=ray(*vp); dup/=np.linalg.norm(dup); e=np.array([1,-0.0156,0.]); e-=(e@dup)*dup; e/=np.linalg.norm(e)
n=np.cross(dup,e); n/=np.linalg.norm(n); n=n if n[2]>0 else -n
P=0.9555*ray(590,481.5)/np.linalg.norm(ray(590,481.5)); d=n@P; dc=d-0.0146
on=lambda x,y,dd,nn: ray(x,y)*dd/(nn@ray(x,y))
# cover ends on slope: measure horizontal extent at rows 366-377 (avoid rounded corners) per row
A=np.load(D+'frames/avg_captured_0023_slope.npy'); R,G,B=A[...,2],A[...,1],A[...,0]
s=G-R
Ls=[]
for y in range(366,378):
    p=s[y-300]
    def cr(xs,lev):
        prev=None
        for x in xs:
            v=p[x-400]
            if prev is not None and (prev-lev)*(v-lev)<=0 and v!=prev: return xp+(lev-prev)/(v-prev)*(x-xp)
            prev=v; xp=x
    xl=cr(range(515,560),14); xr=cr(range(675,630,-1),14)
    Ls.append(np.linalg.norm(on(xr,y,dc,n)-on(xl,y,dc,n)))
    if y%3==0: print('slope row',y,'ends %.1f %.1f'%(xl,xr),'L=%.2f cm'%(100*Ls[-1]))
print('Route A book length median %.2f cm'%(100*np.median(Ls)))
# Route B: table plane
yh=349.9; l=np.array([0,-1.0,yh]); K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); nt=K.T@l; nt/=np.linalg.norm(nt); nt=nt if nt@ray(640,500)>0 else -nt
H=nt@P; Hc=H-0.0146
A=np.load(D+'frames/avg_captured_0023_table.npy'); R,G,B=A[...,2],A[...,1],A[...,0]; s=G-R
Lb=[]
for y in range(484,492):
    p=s[y-300]
    def cr(xs,lev):
        prev=None
        for x in xs:
            v=p[x-400]
            if prev is not None and (prev-lev)*(v-lev)<=0 and v!=prev: return xp+(lev-prev)/(v-prev)*(x-xp)
            prev=v; xp=x
    xl=cr(range(460,520),8); xr=cr(range(690,620,-1),8)
    Lb.append(np.linalg.norm(on(xr,y-0.045*(xr-566),Hc,nt)-on(xl,y-0.045*(xl-566),Hc,nt)))
    if y%2==0: print('table row',y,'ends %.1f %.1f'%(xl,xr),'L=%.2f cm'%(100*Lb[-1]))
print('Route B book length median %.2f cm (H=%.3f)'%(100*np.median(Lb),H))
