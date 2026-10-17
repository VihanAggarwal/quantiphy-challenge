import numpy as np,sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work')
import rect
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
def K1(u,v,f): return np.array([(u-640)/f,(v-360)/f,1.])
def run(v,f=711,scale_mode='lowmid',T=0.015,verbose=True):
    rect.f=f
    board=dict(x=((606.6,467.5),(708.0,492.5),(862.7,361.5),(751.1,360.1)),
               s=((606.6,467.6),(707.7,492.4),(862.9,361.6),(751.1,360.0)),
               o=((606.3,467.5),(710.9,493.2),(863.9,359.9),(753.4,358.2)))[v[-1] if v[-1] in 'xs' else 'o']
    r,P=rect.rect(*board,verbose=False); P=np.array(P)
    lowmid=(P[0]+P[1])/2
    s=0.99/np.linalg.norm(lowmid) if scale_mode=='lowmid' else scale_mode/ P[0][1]  # numeric => camera height of LL
    P=P*s
    n=np.cross(P[1]-P[0],P[3]-P[0]); n/=np.linalg.norm(n)
    d=n@P[0]
    if d>0: n,d=-n,-d       # n points toward camera side: n·0=0 > d
    # book top plane: offset T toward camera: n·X = d + T
    C=np.load(f'{W}/{v}_bookcorners.npy')
    Q=[]
    for (u,vv) in C:
        rr=K1(u,vv,f); t=(d+T)/(n@rr); Q.append(t*rr)
    Q=np.array(Q)  # FL FR BR BL
    L1=np.linalg.norm(Q[1]-Q[0]); L2=np.linalg.norm(Q[2]-Q[3]); W1=np.linalg.norm(Q[3]-Q[0]); W2=np.linalg.norm(Q[2]-Q[1])
    def ang(a,b,c):
        e1=Q[a]-Q[b];e2=Q[c]-Q[b]; return np.degrees(np.arccos(e1@e2/np.linalg.norm(e1)/np.linalg.norm(e2)))
    angs=[ang(3,0,1),ang(0,1,2),ang(1,2,3),ang(2,3,0)]
    if verbose:
        print(f'{v} f={f} T={T} scale={scale_mode}: board W={np.linalg.norm(P[1]-P[0])*100:.1f} L={np.linalg.norm(P[3]-P[0])*100:.1f} cm, LL height={P[0][1]*100:.1f}cm | book front(FL-FR)={L1*100:.2f} back={L2*100:.2f} left(FL-BL)={W1*100:.2f} right(FR-BR)={W2*100:.2f} angles',np.round(angs,1),'ranges',np.round(np.linalg.norm(Q,axis=1),3),'centre range %.3f'%np.linalg.norm(Q.mean(0)))
    return L1,L2,W1,W2,angs,Q
if __name__=='__main__':
    for v in ['captured_0024x','captured_0024s','captured_0024']:
        for T in [0.0,0.015]:
            run(v,T=T)
    for f in [680,740,770]:
        run('captured_0024x',f=f)
    run('captured_0024x',scale_mode=0.155); run('captured_0024x',scale_mode=0.167)
