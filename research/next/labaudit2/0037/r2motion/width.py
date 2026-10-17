import cv2,numpy as np,json,sys
from track import load
tr=json.load(open('tracks.json'))
def measure(sfx,key):
    fr=load(sfx)
    med=np.median(np.stack(fr[::2]),axis=0).astype(np.float32)
    out={}
    for i,r in enumerate(tr[key]):
        if r is None or i<12: continue
        f=fr[i].astype(np.float32)
        # whiteness: min channel (white ball high in all channels), minus background min-channel
        w=f.min(axis=2)
        cxx,cyy=r['cx'],r['cy']
        # local patch
        x0,y0=int(cxx)-45,int(cyy)-45
        P=w[y0:y0+91,x0:x0+91]
        if P.shape!=(91,91): continue
        # orientation from thresholded mask moments
        bg=np.percentile(P,20); pk=np.percentile(P,99)
        m=(P>(bg+pk)/2).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=lab[45,45] if lab[45,45]>0 else 1+np.argmax(st[1:,4])
        mk=(lab==k)
        ys,xs=np.nonzero(mk); mx,my=xs.mean(),ys.mean()
        C=np.cov(np.stack([xs-mx,ys-my]))
        ev,evec=np.linalg.eigh(C)
        dmaj=evec[:,1]; dmin=evec[:,0]
        # sample perpendicular profiles through center, band +-3 px along major
        prof=[]
        s=np.arange(-30,30.01,0.25)
        for a in np.arange(-3,3.01,1.0):
            px=mx+a*dmaj[0]+s*dmin[0]; py=my+a*dmaj[1]+s*dmin[1]
            prof.append(cv2.remap(P,px.astype(np.float32)[None],py.astype(np.float32)[None],cv2.INTER_LINEAR)[0])
        pr=np.mean(prof,0)
        half=(bg+pr.max())/2
        c0=len(pr)//2
        if pr[c0]<=half: continue
        a0=c0
        while a0>0 and pr[a0-1]>half: a0-=1
        a1=c0
        while a1<len(pr)-1 and pr[a1+1]>half: a1+=1
        if a0==0 or a1==len(pr)-1: continue
        # subpixel
        l=s[a0-1]+(half-pr[a0-1])/(pr[a0]-pr[a0-1])*0.25
        rr=s[a1]+(pr[a1]-half)/(pr[a1]-pr[a1+1])*0.25
        width=rr-l
        # length along major
        s2=np.arange(-40,40.01,0.25)
        px=mx+s2*dmaj[0]; py=my+s2*dmaj[1]
        pm=cv2.remap(P,px.astype(np.float32)[None],py.astype(np.float32)[None],cv2.INTER_LINEAR)[0]
        c0=len(pm)//2; b0=c0; b1=c0
        while b0>0 and pm[b0-1]>half: b0-=1
        while b1<len(pm)-1 and pm[b1+1]>half: b1+=1
        length=(b1-b0)*0.25
        out[i]=dict(width=float(width),length=float(length),ang=float(np.degrees(np.arctan2(dmaj[1],dmaj[0]))),cx=float(x0+mx),cy=float(y0+my),area=int(mk.sum()))
    return out
res={}
for sfx,key in [('s','s'),('x','x')]:
    res[key]=measure(sfx,key)
json.dump(res,open('widths.json','w'),indent=1)
for i in sorted(res['s']):
    a=res['s'][i]; b=res['x'].get(i,{})
    print('%2d s: w=%5.1f L=%5.1f c=(%6.1f,%6.1f) | x: w=%5.1f L=%5.1f c=(%6.1f,%6.1f)'%(i,a['width'],a['length'],a['cx'],a['cy'],b.get('width',0),b.get('length',0),b.get('cx',0),b.get('cy',0)))
