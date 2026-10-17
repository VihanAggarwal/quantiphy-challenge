# route 2: centroid of thresholded difference-to-background (last frame), landing spot masked
from util import *
cfg={'0257':(1020,1120,range(1,14)),'0258':(985,1065,range(4,16)),'0259':(815,895,range(1,15)),'0260':(1200,1295,range(6,16))}
for v,(x0,x1,frs) in cfg.items():
    F=frames(v); bg=F[-1].astype(np.int16)
    T=[];Y=[];B=[];Tp=[]
    for i in frs:
        d=np.abs(F[i].astype(np.int16)-bg).max(2)[:790,x0:x1]
        m=(d>35).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,4])
        w=d*(lab==k)
        ys=np.arange(w.shape[0])[:,None]
        cy=(w*ys).sum()/w.sum()
        T.append(i);Y.append(cy);B.append(st[k][1]+st[k][3]);Tp.append(st[k][1])
    T=np.array(T,float);Y=np.array(Y)
    for name,arr in [('wcentroid',Y),('bottom',np.array(B,float)),('top',np.array(Tp,float))]:
        ok=np.ones(len(T),bool)
        if name=='top': ok=np.array(Tp)>2
        p=np.polyfit(T[ok],arr[ok],2); r=arr[ok]-np.polyval(p,T[ok])
        print(v,name,'a=%.4f rms=%.2f t0=%.3f n=%d'%(2*p[0],r.std(),-p[1]/(2*p[0]),ok.sum()))
