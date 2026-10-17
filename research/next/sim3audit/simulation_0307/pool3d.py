import numpy as np,sys,cv2
c=np.array([1280.,720.])
T=np.load('tracks_pool.npy'); src=np.load('src_pool.npy')
F=np.load('pool_fit.npy',allow_pickle=True).item(); e=F['e'];n=F['n'];keep=F['keep'];rr=F['rr']
def body(f,fps,ref=24):
    v=np.array([(e[0]-c[0])/f,(e[1]-c[1])/f,1.]); vh=v/np.linalg.norm(v)
    Vzf=22.16*vh[2]/fps
    a=(e[1]-c[1])/f; up=np.array([0,-1,a]); up/=np.linalg.norm(up)
    s=np.cross(vh,up); s/=np.linalg.norm(s); upo=np.cross(s,vh)
    x=T[:,ref]; Z=Vzf*(n+ref)
    P=np.stack([(x[:,0]-c[0])/f*Z,(x[:,1]-c[1])/f*Z,Z],1)
    return np.stack([P@vh,P@s,P@upo],1),P
if __name__=='__main__':
    for f in [3470,3530,3590]:
      for fps in [24,25]:
        B,P=body(f,fps); B=B[keep]
        fo=B[:,0]; la=B[:,1]; hu=B[:,2]
        lo=np.sort(fo)
        print(f,fps,'fore extent all',(fo.max()-fo.min()).round(2),'(2nd..2nd',(lo[-2]-lo[1]).round(2),') lat extent',(la.max()-la.min()).round(2),'height ext',(hu.max()-hu.min()).round(2))
    B,P=body(3530,24)
    fm=np.median(B[keep,0]); lm=(B[keep,1].max()+B[keep,1].min())/2
    o=np.argsort(B[:,0])
    print('rear-most:')
    for j in [j for j in o if keep[j]][:8]: print('  src',src[j],'fore',(B[j,0]-fm).round(2),'lat',(B[j,1]-lm).round(2),'up',B[j,2].round(2),'px f1',T[j,1].round(0),'rms',rr[j].round(2))
    print('front-most:')
    for j in [j for j in o if keep[j]][-8:]: print('  src',src[j],'fore',(B[j,0]-fm).round(2),'lat',(B[j,1]-lm).round(2),'up',B[j,2].round(2),'px f1',T[j,1].round(0),'rms',rr[j].round(2))
    print('lat extremes:')
    o2=np.argsort(B[:,1]); kk=[j for j in o2 if keep[j]]
    for j in kk[:3]+kk[-3:]: print('  src',src[j],'fore',(B[j,0]-fm).round(2),'lat',(B[j,1]-lm).round(2),'px f1',T[j,1].round(0))
