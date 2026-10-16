import sys, json; sys.path.insert(0,'scripts')
from geo import *
d=json.load(open('xcomps.json'))
def tc(n): return n/25 if n<=11 else ((n+1)/25 if n<=35 else (n+2)/25)
cen={}
for n in range(48):
    bins=[c for c in d[str(n)] if c['a']>4000 and not (abs(c['cx']-986)<5 and abs(c['cy']-370)<5)]
    cen[n]=(bins[0]['cx'],bins[0]['cy'],bins[0]['w'],bins[0]['h'],bins[0]['a'])
for name,dn in [('roll',DOWN_ROLL),('noroll',DOWN_NOROLL)]:
    Pb=P(666.4,617.9,2.082); H=Pb@dn+0.018
    p10=P(*cen[10][:2],2.73); z=H-p10@dn
    pts={n:floor_pt(cen[n][0],cen[n][1],H,dn,z) for n in cen}
    print(name,'z',round(z,3))
    for n in range(0,47):
        dt=tc(n+1)-tc(n)
        v=np.linalg.norm(pts[n+1]-pts[n])/dt
        if n%3==0 or n in (10,11,33,34): print('  n%2d t=%.2f range %.3f v_fwd %.3f  disp_from10 %.3f'%(n,tc(n),np.linalg.norm(pts[n]),v,np.linalg.norm(pts[n]-pts[10])))
    print('  disp 0.4->1.4 (n10->n34) %.3f ; n10->n33 %.3f ; n10->n35 %.3f'%(np.linalg.norm(pts[34]-pts[10]),np.linalg.norm(pts[33]-pts[10]),np.linalg.norm(pts[35]-pts[10])))
