# Expected item score of candidate answers for the white-ball v(1.5) rows under the labnoise click/ToF model
# (research/labnoise/labmodel.py: sigma_px on each click, sigma_z on each depth; forward difference at 25 fps).
# Geometry: ball surface point at c38 (stated 1.353) and velocity from the routes; also the c37 convention.
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge'); sys.path.insert(0,'/home/user/quantiphy-challenge/research/labnoise')
import numpy as np
from labmodel import speed_labels
from qp.mra import item_scores
u=np.array([0.1146,0.1023,1.0]); u/=np.linalg.norm(u); p=1.353*u
def vel(radial,lat):
    # lateral direction: in image plane mostly +x, slight +y; orthogonalise to u
    e=np.array([1.0,0.30,0.0]); e-= (e@u)*u; e/=np.linalg.norm(e)
    return (radial*u+lat*e)/100.
scen={'c38 plane (66)':vel(-61.5,23.5),'c38 size (74)':vel(-70,23.5),'c37 (88)':vel(-83,31)}
cands=[49.6,60,64,66,68,70,74,80]
for sz in [0.005,0.01,0.02]:
    print('sigma_z=%.3f sigma_px=2'%sz)
    for nm,v in scen.items():
        L=100*speed_labels(p,v,2.0,sz,n=20000,seed=1)
        sc=[np.nanmean(item_scores(np.full(len(L),c),L)) for c in cands]
        print('  %-15s label median %.1f mean %.1f | '%(nm,np.median(L),L.mean())+' '.join('%g:%.3f'%(c,s) for c,s in zip(cands,sc)))
