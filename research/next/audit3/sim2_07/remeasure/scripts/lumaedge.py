import cv2, numpy as np, json, sys
vid=sys.argv[1]; ell=json.load(open(sys.argv[2])); lo,hi=[int(x) for x in sys.argv[3].split(',')]
E={int(r[0]):r for r in ell}
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg=np.median(np.stack(fr[0:12]),axis=0).astype(np.float32)
def remap(img,px,py): return cv2.remap(img,px.astype(np.float32),py.astype(np.float32),cv2.INTER_CUBIC)
res=[]
for i in range(lo,hi+1):
    if i not in E: continue
    _,cx,cy=E[i][:3]
    f=fr[i].astype(np.float32)
    Y=f@np.array([0.114,0.587,0.299],np.float32)
    Yb=bg@np.array([0.114,0.587,0.299],np.float32)
    D=Yb-Y   # positive where darker than background
    angs=np.radians(np.arange(0,360,5)); r=np.arange(4,20,0.1)
    PX=cx+np.cos(angs)[:,None]*r[None,:]; PY=cy+np.sin(angs)[:,None]*r[None,:]
    prof=remap(D,PX,PY)
    Bprof=remap(bg[...,0]-f[...,0],PX,PY)
    edges=[];bedges=[]
    for k,a in enumerate(angs):
        p=prof[k]; 
        inner=np.median(p[(r>=6)&(r<=9)])   # ball interior contrast
        # first crossing of half of inner below, going outward, beyond r=9
        half=inner/2
        idx=np.where((r>9)&(p<half))[0]
        e=np.nan
        if inner>8 and len(idx):
            j=idx[0]; e=r[j-1]+(p[j-1]-half)/(p[j-1]-p[j])*(r[j]-r[j-1])
        edges.append(e)
        q=Bprof[k]; inb=np.median(q[(r>=4)&(r<=8)]); hb=inb/2
        idb=np.where((r>8)&(q<hb))[0]; eb=np.nan
        if len(idb): j=idb[0]; eb=r[j-1]+(q[j-1]-hb)/(q[j-1]-q[j])*(r[j]-r[j-1])
        bedges.append(eb)
    edges=np.array(edges); bedges=np.array(bedges)
    deg=np.degrees(angs)
    # slope direction ~44.2 deg (down-right) and 224.2 (up-left); perpendicular 134.2 (down-left, toward slope?) and 314.2 (up-right)
    def sel(center,half=20):
        dd=np.abs(((deg-center+180)%360)-180); return dd<=half
    out={}
    for nm,cen in (('along+',44.2),('along-',224.2),('perpDL',134.2),('perpUR',314.2)):
        m=sel(cen)
        out[nm]=(np.nanmedian(edges[m]),np.nanmedian(bedges[m]))
    res.append((i,out))
    print(i,' '.join(f"{k}: Y={v[0]:.2f} B={v[1]:.2f}" for k,v in out.items()),
          f"| Ydiam_along={out['along+'][0]+out['along-'][0]:.2f} Bdiam_along={out['along+'][1]+out['along-'][1]:.2f} Ydiam_perp={out['perpDL'][0]+out['perpUR'][0]:.2f} Bdiam_perp={out['perpDL'][1]+out['perpUR'][1]:.2f}")
