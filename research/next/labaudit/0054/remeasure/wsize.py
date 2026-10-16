import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
from geom import comps
from ba import *
from pts import *
from sizes import width
A=[];B=[];lab=[]
for nm,da,db in [('W',aW,bW),('G',aG,bG),('O',aO,bO)]:
    for k in sorted(set(da)&set(db)):
        A.append(da[k]);B.append(db[k]);lab.append((nm,k))
xa=np.array(A,float); xb=np.array(B,float); idx={l:i for i,l in enumerate(lab)}
R,t,_,X,res=solve(xa,xb,fb0=711.,fit_fb=False)
s=4.1
rat=[];absW=[];absG=[]
for k in range(25,36):
    if ('W',k) not in idx or ('G',k) not in idx: continue
    XW=X[idx[('W',k)]]*s; XG=X[idx[('G',k)]]*s
    for cam,v,dW,dG,f,RR,tt in [('a','ax',aW,aG,711.,np.eye(3),np.zeros(3)),('b','bx',bW,bG,711.,R,t*s)]:
        wW=width(v,k,dW[k]); wG=width(v,k,dG[k])
        if wW is None or wG is None: continue
        rW=np.linalg.norm(RR@XW+tt); rG=np.linalg.norm(RR@XG+tt)
        r=(wW[0]*rW)/(wG[0]*rG)
        DW=wW[0]*rW/f*100; DG=wG[0]*rG/f*100
        rat.append((cam,k,r)); absW.append((cam,k,DW)); absG.append((cam,k,DG))
        print(f'{cam} frame {k}: W width {wW[0]:.1f}px r={rW:.2f}m -> {DW:.2f}cm | G width {wG[0]:.1f}px r={rG:.2f}m -> {DG:.2f}cm | ratio W/G={r:.3f}')
ra=np.array([x[2] for x in rat]); print('ratio W/G median %.3f mean %.3f sd %.3f'%(np.median(ra),ra.mean(),ra.std()))
for cam in 'ab':
    rr=np.array([x[2] for x in rat if x[0]==cam]); print(cam,'ratio median %.3f'%np.median(rr), ' absW median %.2f absG median %.2f'%(np.median([x[2] for x in absW if x[0]==cam]),np.median([x[2] for x in absG if x[0]==cam])))
