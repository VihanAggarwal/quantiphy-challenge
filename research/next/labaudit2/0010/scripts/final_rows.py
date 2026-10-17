"""Label-style values for v(0.6), a(0.6), v(0.3), a(0.3) by route, with the s-render clicks.
Label: P(c0)=stated*ray(click c0); P(c0+j)=(stated + dR route(c0->c0+j))*ray(click) [persist];
v=25|P1-P0|, a_vec=625|P2-2P1+P0|, a_sp=25(|P2-P1|-|P1-P0|)*25/25.
Routes for dR: (1) dynamic pendulum fits (pend3d_v3 variants), (2) geometric sphere with the string-line pivot
(640.3,234.1), (d0,L) from anchors / sizes, (3) size-only local polynomial (half-max, s-circle)."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
import geo
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
T=json.load(open(B+'track.json')); S=json.load(open(B+'size_s.json')); Cc=json.load(open(B+'circ.json'))
k=np.arange(49); n=np.array([cap(i) for i in k])
u=np.array([T['s'][i]['u'] for i in k]); v=np.array([T['s'][i]['v'] for i in k])
kof={c:i for i,c in zip(k,n)}
def lab(c0,stated,dR):   # dR: radial steps (c0->c0+1, c0+1->c0+2) in m
    R=[stated,stated+dR[0],stated+dR[0]+dR[1]]
    P=[R[j]*ray(u[kof[c0+j]],v[kof[c0+j]]) for j in range(3)]
    v1=25*np.linalg.norm(P[1]-P[0]); v2=25*np.linalg.norm(P[2]-P[1])
    return v1,625*np.linalg.norm(P[2]-2*P[1]+P[0]),25*(v2-v1)
rows=[]
def add(route,c0,stated,dR):
    v1,av,asp=lab(c0,stated,dR); rows.append((route,c0,dR[0]*100,dR[1]*100,v1,av,asp))
# (1) dynamic
D3=json.load(open(B+'pend3d_v3.json'))
for nm,d in D3.items():
    R=np.array(d['R'])
    for c0,st in ((15,1.344),(8,1.706),(7,1.706)):
        add('dyn:'+nm,c0,st,(R[c0+1]-R[c0],R[c0+2]-R[c0+1]))
# (2) geometric sphere with fixed pivot pixel
PIV=(640.3,234.1)
pu=np.full(49,PIV[0]); pv=np.full(49,PIV[1])
def gr(d0,L): return geo.ranges(d0,L,pu=pu,pv=pv)[0]
for kind in ('anch','size'):
    if kind=='anch':
        idx=[(8,1.706),(14,1.344),(29,1.784)]   # first period, off the tangency
        cost=lambda d0,L: sum((gr(d0,L)[i]-0.035-s)**2 for i,s in idx)
    else:
        good=np.array([(nn<=10 or 15<=nn<=20 or 25<=nn<=32) for nn in n])
        w=np.array([S[i]['wh'] for i in k])
        cost=lambda d0,L: np.sum(((F*0.07/gr(d0,L)-w)[good])**2)
    c,d0,L=geo.grid_fit(cost,d0s=np.arange(1.40,1.65,0.0025),Ls=np.arange(0.30,0.40,0.001))
    R=gr(d0,L); D=geo.ranges(d0,L,pu=pu,pv=pv)[1]
    print(f"geo {kind}: d0 {d0:.4f} L {L:.3f}  sqrt(disc) c15..c17 {np.sqrt(np.maximum(D[[14,15,16]],0))*100}")
    for c0,st in ((15,1.344),(8,1.706),(7,1.706)):
        i=kof[c0]; add(f'geo:{kind}',c0,st,(R[kof[c0+1]]-R[i],R[kof[c0+2]]-R[kof[c0+1]]))
# (3) size-only local polynomials
for nm,wd in (('halfmax',np.array([S[i]['wh'] for i in k])),('s_circle',np.array([Cc[i]['s']['d'] for i in k]))):
    Rz=F*0.07/wd
    for (lo,hi,deg,cen,c0) in ((13,23,2,18.,15),(12,24,4,18.,15),(14,22,2,18.,15),(4,11,2,8.,8),(3,11,3,8.,8),(4,11,2,8.,7),(3,11,3,8.,7)):
        sel=(n>=lo)&(n<=hi); p=np.polyfit(n[sel]-cen,Rz[sel],deg); f=lambda x: np.polyval(p,x-cen)
        add(f'size:{nm}:c{lo}-{hi}d{deg}',c0,{15:1.344,8:1.706,7:1.706}[c0],(f(c0+1)-f(c0),f(c0+2)-f(c0+1)))
print(f"{'route':34s} c0  dR1   dR2    v_label  a_vec  a_speed")
for r in rows:
    print(f"{r[0]:34s} c{r[1]:2d} {r[2]:+5.2f} {r[3]:+5.2f}   {r[4]:.3f}   {r[5]:5.2f}  {r[6]:+6.2f}")
json.dump(rows,open(B+'final_rows.json','w'))
