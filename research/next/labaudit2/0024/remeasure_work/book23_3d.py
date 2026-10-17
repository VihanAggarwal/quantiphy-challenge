import numpy as np,sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work')
import rect
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
def K1(u,v,f): return np.array([(u-640)/f,(v-360)/f,1.])
def run(C_book,f=711,T=0.015,scale=None,board='captured_0023x',verbose=True,tag=''):
    rect.f=f
    B=np.load(f'{W}/{board}_board.npy')
    r,P=rect.rect(*[tuple(c) for c in B],verbose=False); P=np.array(P)
    # scale: camera height above table at the board low edge (LL,LR on table) or lowmid range
    if scale is None: s=0.16/((P[0][1]+P[1][1])/2)
    elif scale[0]=='range_lowmid': s=scale[1]/np.linalg.norm((P[0]+P[1])/2)
    elif scale[0]=='h': s=scale[1]/((P[0][1]+P[1][1])/2)
    P=P*s
    n=np.cross(P[1]-P[0],P[3]-P[0]); n/=np.linalg.norm(n); d=n@P[0]
    if d>0: n,d=-n,-d
    Q=np.array([((d+T)/(n@K1(u,v,f)))*K1(u,v,f) for u,v in C_book])
    L1=np.linalg.norm(Q[1]-Q[0]); L2=np.linalg.norm(Q[2]-Q[3]); W1=np.linalg.norm(Q[3]-Q[0]); W2=np.linalg.norm(Q[2]-Q[1])
    if verbose: print(f'{tag} f={f} T={T} scale={scale}: board W={np.linalg.norm(P[1]-P[0])*100:.1f} L={np.linalg.norm(P[3]-P[0])*100:.1f} lowmid range {np.linalg.norm((P[0]+P[1])/2):.3f} h={P[0][1]:.3f} | book L={L1*100:.2f}/{L2*100:.2f} W={W1*100:.2f}/{W2*100:.2f} W/L={(W1+W2)/(L1+L2):.3f} centre range {np.linalg.norm(Q.mean(0)):.3f}')
    return (L1+L2)/2,(W1+W2)/2
if __name__=='__main__':
    yb=350.3; yf_l=380.2; yf_r=379.3
    for xl,xr in [(531,651),(529,652),(533,650)]:
        C=[(xl-0.3,yf_l),(xr+0.5,yf_r),(xr,yb),(xl,yb)]
        run(C,tag=f'xl={xl} xr={xr}')
    C=[(530.7,yf_l),(651.5,yf_r),(651,yb),(531,yb)]
    for f in [680,740,770]: run(C,f=f,tag='f-sens')
    for T in [0.0,0.02]: run(C,T=T,tag='T-sens')
    run(C,scale=('range_lowmid',0.9555),tag='scale slope_near=0.9555')
    run(C,scale=('h',0.15),tag='h=0.15'); run(C,scale=('h',0.17),tag='h=0.17')
    run(C,board='captured_0023s',tag='s-board')
