import numpy as np
E=np.array([-765.,-483.]); C=np.array([1280.,720.])
def fitq(P,e=E,minlen=30,i0=1):
    out=[]
    for j in range(P.shape[1]):
        ok=np.isfinite(P[:,j,0]); ok[:i0]=False
        if ok.sum()<minlen: continue
        i=np.nonzero(ok)[0]; xy=P[ok,j]
        rho=np.linalg.norm(xy-e,axis=1)
        A=np.c_[np.ones(len(i)),i]
        coef=np.linalg.lstsq(A,1/rho,rcond=None)[0]
        pred=1/(A@coef)
        res=np.sqrt(np.mean((pred-rho)**2))
        # perpendicular residual to line through e
        d=(xy-e); u=d.mean(0)/np.linalg.norm(d.mean(0)); perp=np.sqrt(np.mean((d@np.array([-u[1],u[0]]))**2))
        q=coef[1]/coef[0]
        out.append(dict(j=j,q=q,R=1/coef[0],res=res,perp=perp,n=ok.sum(),xy=xy,i=i,u=u))
    return out
def pos3d(tr,f,iref,vzf,e=E):
    # image position at iref from model
    x=e+tr['u']*tr['R']/(1+tr['q']*iref)
    Z=vzf*(1/tr['q']+iref)
    X=(x[0]-C[0])*Z/f; Y=(x[1]-C[1])*Z/f
    return np.array([X,Y,Z]),x
if __name__=='__main__':
    for c in ['0303','0305','0307']:
        P=np.load(f'tracks_{c}.npy')
        T=fitq(P)
        q=np.array([t['q'] for t in T]); res=np.array([t['res'] for t in T]); perp=np.array([t['perp'] for t in T])
        print(c,len(T),'q med',np.median(q),'q range',np.percentile(q,[5,95]),'res med',np.median(res),'perp med',np.median(perp))
