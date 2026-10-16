# half-contrast edge widths of the small balls in the ORIGINAL renders (not SAM masks)
HALF=18
import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure')
import cv2,numpy as np
from pts import *
D='/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/frames'
def fwhm_extent(img,c,direction,half=18):
    global HALF
    half=HALF
    # sample along a line through c in 'direction', 0.25px steps; per-channel colour distance to local background
    c=np.array(c,float); d=np.array(direction,float); d/=np.linalg.norm(d)
    ts=np.arange(-half,half+0.01,0.25)
    pts=c[None]+ts[:,None]*d[None]
    mx=pts[:,0].astype(np.float32).reshape(1,-1); my=pts[:,1].astype(np.float32).reshape(1,-1)
    vals=cv2.remap(img.astype(np.float32),mx,my,cv2.INTER_LINEAR)[0]
    bg=np.r_[vals[:12],vals[-12:]].mean(0)
    dist=np.linalg.norm(vals-bg,axis=1)
    # average perpendicular offsets to reduce noise
    pk=dist[np.abs(ts)<3].max(); thr=pk/2
    inside=np.where(dist>thr)[0]
    if len(inside)==0: return None
    i0,i1=inside[0],inside[-1]
    # subpixel interpolate
    def interp(i,j):
        a,b=dist[i],dist[j]; return ts[i]+(thr-a)/(b-a+1e-9)*(ts[j]-ts[i])
    if i0==0 or i1==len(dist)-1: return None
    lo=interp(i0-1,i0); hi=interp(i1,i1+1)
    return hi-lo
def multi(img,c,direction,offs=(-2,-1,0,1,2)):
    d=np.array(direction,float); d/=np.linalg.norm(d); p=np.array([-d[1],d[0]])
    w=[fwhm_extent(img,np.array(c)+o*p*0.0,d) for o in [0]]
    # take max over parallel lines (the diameter chord is the widest)
    ws=[fwhm_extent(img,np.array(c)+o*p,d) for o in offs]
    ws=[x for x in ws if x is not None]
    return max(ws) if ws else None
for v,dW,dG,HALF in [('a',aW,aG,16),('b',bW,bG,34)]:
    for k in range(25,36):
        if k not in dW or k not in dG: continue
        img=cv2.imread(f'{D}/{v}_{k:02d}.png')
        out=[]
        for nm,dd in [('W',dW),('G',dG)]:
            c=dd[k]
            # motion direction from neighbours
            kk=[j for j in (k-1,k+1) if j in dd]
            mv=np.array(dd[max(kk)])-np.array(dd[min(kk)]) if len(kk)==2 else np.array([1.,0.])
            perp=np.array([-mv[1],mv[0]])
            w=multi(img,c,perp)
            out.append((nm,w))
        print(v,k,' '.join(f'{nm} perp-width={w:.1f}px' if w else f'{nm} None' for nm,w in out), ' ratio W/G=%.3f'%(out[0][1]/out[1][1]) if out[0][1] and out[1][1] else '')
