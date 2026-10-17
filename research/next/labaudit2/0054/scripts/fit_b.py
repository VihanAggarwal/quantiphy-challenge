from common import *
from tracks import *
from fit_a import fit, model, gd
dvp=np.load(OUT+'/b_down.npy')
def gr1(p=29.9,r=-6.5):
    p=np.radians(p); r=np.radians(r); return np.array([np.sin(r)*np.cos(p),np.cos(r)*np.cos(p),np.sin(p)])
for gname,gdir in [('vp',dvp),('r1',gr1()),('p27',gr1(27,-7.9)),('p35',gr1(35,-7.9))]:
    for name,tr,ks in [('white',B_W,list(range(24,39))),('green',B_G,list(range(24,37)))]:
        p,rms=fit(tr,ks,gdir)
        C=lambda t: model(p,np.array([t]),1.0,gdir)[0]
        rng=lambda t: np.linalg.norm(C(t))
        v=lambda t: np.linalg.norm(p[3:6]+9.81*gdir*(t-1.0))
        print(f'{gname} {name} rms={rms:.2f} range(1.0)={rng(1.0):.3f} r(1.52)={rng(1.52):.3f} |v|(1.0)={v(1.0):.2f} v(1.5)={v(1.5):.2f} v(1.52)={v(1.52):.2f} fd25-26={np.linalg.norm(C(1.04)-C(1.0))*25:.2f} fd38-39={np.linalg.norm(C(1.56)-C(1.52))*25:.2f} fd37-38={np.linalg.norm(C(1.52)-C(1.48))*25:.2f}')
