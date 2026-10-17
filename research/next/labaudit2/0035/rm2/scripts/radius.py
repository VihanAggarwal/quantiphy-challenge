# Subpixel radius of soccer ball via radial alpha-0.5 crossings + circle fit, in ax and as renders.
import cv2, numpy as np, json
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0035/rm2/track_ax.json'))
def cap(i): return int(np.floor(i*25/24+0.5))
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0035{v}.mp4'); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
def alpha_ax(f):
    b,g,r=[f[...,k].astype(np.float32) for k in range(3)]
    gn=g-np.maximum(r,b)   # ~200+ for green bg, <~50 for ball
    return np.clip((180-gn)/150,0,1)
def circfit(x,y):
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x**2+y**2
    sol=np.linalg.lstsq(A,b,rcond=None)[0]; xc,yc=sol[0],sol[1]; r=np.sqrt(sol[2]+xc**2+yc**2)
    return xc,yc,r
res={}
for v in ['ax']:
    F=frames(v)
    for i in range(21,48):
        d=T[str(i)].get('sb')
        if not d: continue
        a=alpha_ax(F[i]); a=cv2.GaussianBlur(a,(0,0),0.7)
        cx0,cy0=d['cxw'],d['cyw']
        xs=[];ys=[]
        for th in np.linspace(0,2*np.pi,90,endpoint=False):
            rr=np.arange(10,40,0.25)
            px=cx0+rr*np.cos(th); py=cy0+rr*np.sin(th)
            vals=cv2.remap(a,px.astype(np.float32)[None,:],py.astype(np.float32)[None,:],cv2.INTER_LINEAR)[0]
            k=np.where((vals[:-1]>=0.5)&(vals[1:]<0.5))[0]
            if len(k)==0: continue
            k=k[0]; t=(vals[k]-0.5)/(vals[k]-vals[k+1]); r0=rr[k]+t*0.25
            xs.append(cx0+r0*np.cos(th)); ys.append(cy0+r0*np.sin(th))
        xs=np.array(xs); ys=np.array(ys)
        xc,yc,r=circfit(xs,ys)
        resid=np.hypot(xs-xc,ys-yc)-r
        keep=abs(resid)<2.5*np.median(abs(resid))+0.3
        xc,yc,r=circfit(xs[keep],ys[keep])
        res[i]=(cap(i),xc,yc,2*r,keep.sum())
for i,(j,xc,yc,d,n) in res.items(): print('v%2d j%2d circ centre (%.2f,%.2f) diam %.2f n%d  | deq %.2f'%(i,j,xc,yc,d,n,T[str(i)]['sb']['dsoft']))
json.dump({str(k):[float(x) for x in v] for k,v in res.items()},open('/home/user/quantiphy-challenge/research/next/labaudit2/0035/rm2/radius_ax.json','w'))
# linear fit of log diameter over capture 31..49
J=np.array([v[0] for v in res.values()]); D=np.array([v[3] for v in res.values()])
for a,b in ((31,49),(33,49),(35,46),(36,46),(27,49)):
    m=(J>=a)&(J<=b); p=np.polyfit(J[m]/25.,np.log(D[m]),1)
    print('j%d-%d dlnD/dt=%.4f /s -> range-rate at rho=3.147: %.1f cm/s'%(a,b,p[0],-p[0]*3.147*100))
