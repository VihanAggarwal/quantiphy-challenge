import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0035/scripts')
from recon import *
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
trx=load('bx')
def pix(key,t):
    x=t*24; i0=int(np.floor(x)); a=x-i0; d=trx[key]
    return (1-a)*d[i0]['cx']+a*d[i0+1]['cx'],(1-a)*d[i0]['cy']+a*d[i0+1]['cy']
Rb,Rs=0.116,0.0905
St=[(0.9,'sb',2.477),(0.9,'bb',2.7777),(1.4,'bb',2.602),(1.4,'sb',2.373)]
pts=[(r*ray(*pix(key,t)),Rb if key=='bb' else Rs) for t,key,r in St]
def heights(n):
    return np.array([-(n@P)+R for P,R in pts])
# route 2: free plane from 4 stated pts (3 params: normal 2 + H) via least squares on heights
bestg=None
for th in np.radians(np.arange(0,70,0.1)):
    for ph in np.radians(np.arange(0,360,0.5)):
        n=np.array([np.sin(th)*np.cos(ph),-np.cos(th),np.sin(th)*np.sin(ph)])
        h=heights(n); sd=h.std()
        if bestg is None or sd<bestg[0]: bestg=(sd,n,h.mean(),h)
sd2,n2,H,h2=bestg
print('route2 stated-only plane n',np.round(n2,4),'H %.3f'%H,'resid cm',np.round(100*(h2-H),2))
# list near-optimal set spread

# route 3: corner family (L,R orthogonal) + stated heights
fam=np.load(f'{S}/fam_b.npy')
best=None
for row in fam:
    n=row[1:]; h=heights(n); sd=h.std()
    if best is None or sd<best[0]: best=(sd,n,h.mean())
sd,n3,H3=best
print('route3 corner-family+stated n',np.round(n3,4),'H %.3f'%H3,'height sd cm %.2f'%(100*sd))
n1=np.array([-0.1146,-0.8224,-0.5573]); print('corner(L,R,V) n',n1,'H %.3f sd %.2f'%(heights(n1).mean(),100*heights(n1).std()))
for nm,n,HH in [('route2',n2,H),('route3',n3,H3),('cornerV',n1,heights(n1).mean())]:
    def onp(u,v,R): r=ray(u,v); t=-(HH-R)/(n@r); return t*r
    p0=onp(828.4,280.0,Rb); p1=onp(*pix('bb',0.9),Rb)
    s0=onp(436.5,685.7,Rs); s1=onp(*pix('sb',0.9),Rs)
    print(nm,'bb rest range %.3f -> disp %.1f cm | sb rest range %.3f -> disp %.1f'%(np.linalg.norm(p0),100*np.linalg.norm(p1-p0),np.linalg.norm(s0),100*np.linalg.norm(s1-s0)), 'angle to cornerV %.1f deg'%np.degrees(np.arccos(min(1,abs(n@n1)))))
# size route
for d_rest in [52.7,53.3,54.0]:
    r0=711*0.232/d_rest; p0=r0*ray(828.4,280.0); p1=2.7777*ray(*pix('bb',0.9))
    print('size route d_rest %.1f r0 %.3f disp %.1f'%(d_rest,r0,100*np.linalg.norm(p1-p0)))
