from util import *
for v in ['0257','0258','0259','0260']:
    F=frames(v); g=np.mean([F[i].astype(float) for i in (0,39)],0).mean(2)
    gs=cv2.GaussianBlur(g,(0,0),0.8)
    gx=np.diff(gs,axis=1)
    pts=[]
    for y in range(866,894):
        # expected x ~ 1525+0.5*(y-866); search +-4
        xe=1525+0.5*(y-866); a=int(xe-5); b=int(xe+6)
        pr=gx[y,a:b]
        i=int(np.argmax(pr))
        if pr[i]<3: continue
        if 0<i<len(pr)-1:
            p0,p1,p2=pr[i-1],pr[i],pr[i+1]; d=0.5*(p0-p2)/(p0-2*p1+p2)
        else: d=0
        pts.append((y,a+i+0.5+d,pr[i]))
    P=np.array(pts)
    p=np.polyfit(P[:,0],P[:,1],1)
    res=P[:,1]-np.polyval(p,P[:,0])
    ok=np.abs(res)<1.5
    p=np.polyfit(P[ok,0],P[ok,1],1)
    xb=np.polyval(p,864.84); xf=np.polyval(p,895.39)
    print(v,'n=%d slope=%.3f  x@back=%.2f x@front=%.2f  ratio(cx=960)=%.4f  ratio using front-face end 1538.5: %.4f'%(ok.sum(),p[0],xb,xf,(xb-960)/(xf-960),(xb-960)/(1538.5-960)))
