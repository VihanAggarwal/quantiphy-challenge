import cv2, numpy as np, json, sys
def map_coordinates(img,coords,order=1):
    py,px=coords
    return cv2.remap(img,np.asarray(px,np.float32).reshape(1,-1),np.asarray(py,np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]
vid=sys.argv[1]; tr=json.load(open(sys.argv[2])); bgr=sys.argv[3].split(',')
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
S=[cv2.cvtColor(f,cv2.COLOR_BGR2HSV)[...,1].astype(np.float32) for f in fr]
bg=np.median(np.stack([S[i] for i in range(int(bgr[0]),int(bgr[1]))]),axis=0)
def fwhm(p):
    p=np.asarray(p); mx=p.max(); half=mx/2
    above=np.where(p>=half)[0]; a,b=above[0],above[-1]
    # subpixel interpolation
    l=a-1+(half-p[a-1])/(p[a]-p[a-1]) if a>0 else a
    r=b+(p[b]-half)/(p[b]-p[b+1]) if b<len(p)-1 else b
    return r-l
out=[]
for k,r in tr.items():
    i=int(k)
    if r is None or r['area']<500: continue
    d=S[i]-bg
    cx,cy=r['cx'],r['cy']
    # refine center by saturation-weighted centroid
    h=22
    y0,y1=int(cy)-h,int(cy)+h; x0,x1=int(cx)-h,int(cx)+h
    if y0<0 or x0<0 or y1>1080 or x1>1920: continue
    W=np.clip(d[y0:y1,x0:x1],0,None); 
    mx=np.percentile(W,99.5)
    Wt=np.clip(W-0.25*mx,0,None)
    yy,xx=np.mgrid[y0:y1,x0:x1]
    scx=(Wt*xx).sum()/Wt.sum(); scy=(Wt*yy).sum()/Wt.sum()
    # half-max area
    core=np.median(W[W>0.8*mx])
    area=(W>=core/2).sum()
    res={}
    t=np.linspace(-20,20,401)
    for name,(ux,uy) in dict(h=(1,0),v=(0,1),d1=(0.7071,0.7071),d2=(0.7071,-0.7071)).items():
        prof=[]
        for off in np.linspace(-3,3,7):
            px=scx+t*ux-off*uy; py=scy+t*uy+off*ux
            prof.append(map_coordinates(d,[py,px],order=1))
        p=np.mean(prof,axis=0)  # average across 7 parallel lines near center -> slight underestimate; use central only too
        pc=map_coordinates(d,[scy+t*uy,scx+t*ux],order=1)
        pc=np.clip(pc,0,None)
        res[name]=fwhm(pc)*(t[1]-t[0])
    out.append((i,scx,scy,2*np.sqrt(area/np.pi),res))
    print(i,f'{scx:.2f} {scy:.2f} eqd={2*np.sqrt(area/np.pi):.2f} core={core:.0f}',' '.join(f'{n}={v:.2f}' for n,v in res.items()))
json.dump(out,open(sys.argv[4],'w'))
