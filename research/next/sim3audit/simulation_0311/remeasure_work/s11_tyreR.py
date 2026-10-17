import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work')
from recon import *
f=float(sys.argv[1]) if len(sys.argv)>1 else 4240.
K,Ki,D,L,U=cam(f)
H=json.load(open(W+'hubs.json'))
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0311.mp4')
fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0))
rhos=np.linspace(0.035,0.085,101)
for nm,krange in [('RW',range(28,66,2)),('FW',range(14,56,2))]:
    Q,_=tri({int(k):v for k,v in H[nm].items()},f)
    tab={}
    for th_deg in range(0,360,15):
        th=np.radians(th_deg); est=[]
        for k in krange:
            P0=Q+(k-24)/24*D
            pts=[]
            for rho in rhos:
                P=P0+rho*(np.cos(th)*D+np.sin(th)*U); p=K@P; pts.append(p[:2]/p[2])
            pts=np.float32(pts)
            prof=cv2.remap(fr[k],pts[:,0].reshape(1,-1),pts[:,1].reshape(1,-1),cv2.INTER_LINEAR).ravel()
            g=np.gradient(prof)
            # rim edge: most negative gradient for rho<0.056 ; tyre outer edge: max positive gradient after rim edge
            i_rim=np.argmin(g[:45]) 
            j=i_rim+5+np.argmax(g[i_rim+5:])
            est.append((rhos[i_rim],rhos[j],g[j],prof[min(j+5,100)]-prof[max(j-5,0)]))
        e=np.array(est)
        tab[th_deg]=(np.median(e[:,0]),np.median(e[:,1]),np.median(e[:,3]))
    print(nm)
    for th,(a,b,cst) in tab.items(): print('  th %3d  rim %.4f  tyre %.4f  contrast %.1f'%(th,a,b,cst))
