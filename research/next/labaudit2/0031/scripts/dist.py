"""Ball-ball distance at t=1.6 s (video k38 = capture n40), label-style: clicks at centres, stated ranges."""
import numpy as np, json
B='/home/user/quantiphy-challenge/research/next/labaudit2/0031/'
co=json.load(open(B+'chords_o.json')); cx=json.load(open(B+'chords_x.json'))
def c(ball,k): a,b=co[k][ball],cx[k][ball]; return np.array([0.5*(a['xc']+b['xc']),0.5*(a['yc_fit']+b['yc_fit'])])
def ray(p,F):
    v=np.array([(p[0]-640)/F,(p[1]-360)/F,1.]); return v/np.linalg.norm(v)
for k in (37,38,39):
    t,w=c('T',k),c('W',k)
    for F in (650,711,760):
        a=np.linalg.norm(99.4*ray(t,F)-119.0*ray(w,F)); b=np.linalg.norm(119.0*ray(t,F)-99.4*ray(w,F))
        print('k%d F%d  swapped(T .994,W 1.19)=%.2f  literal(T 1.19,W .994)=%.2f  px sep=%.1f'%(k,F,a,b,np.linalg.norm(t-w)))
# physical centre-centre (routes) at k38
R=json.load(open(B+'routes_f711.json'))
for key in ('Ps','Pp'):
    PT={r['k']:np.array(r[key]) for r in R['T']}; PW={r['k']:np.array(r[key]) for r in R['W']}
    print(key,'centre-centre k38: %.2f'%np.linalg.norm(PT[38]-PW[38]))
# MC with click jitter 2px
rng=np.random.default_rng(0); t,w=c('T',38),c('W',38); L=[]
for i in range(20000):
    tt=t+rng.normal(0,2,2); ww=w+rng.normal(0,2,2)
    L.append(np.linalg.norm(99.4*ray(tt,711)-119.0*ray(ww,711)))
L=np.array(L); print('MC click 2px: median %.2f p10 %.2f p90 %.2f'%(np.median(L),*np.percentile(L,[10,90])))
