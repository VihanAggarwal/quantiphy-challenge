import numpy as np, cv2
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
o=np.load(S+'o.npy'); s=np.load(S+'s.npy'); x=np.load(S+'x.npy')
def edges(g,r,c0,c1):
    p=g[r,c0:c1].astype(float)
    # bright plateau of box
    hi=np.percentile(p,80)
    return p,hi
def crossings(p,lev):
    out=[]
    for k in range(len(p)-1):
        if (p[k]-lev)*(p[k+1]-lev)<0:
            out.append(k+(lev-p[k])/(p[k+1]-p[k]))
    return out
np.set_printoptions(linewidth=250,precision=1,suppress=True)
for name,V in [('o',o),('s',s),('x',x)]:
    W=[];LE=[];RE=[]
    for i in range(0,29):
        g=V[i].astype(float).mean(axis=2)
        # find box columns: rows 256..282
        for r in range(254,284,2):
            p=g[r,460:500]
            # right edge: last crossing of level halfway between box plateau and background to the right
            box=np.median(p[12:24]); bgR=np.median(g[r,496:502])
            levR=(box+bgR)/2
            cr=[c for c in crossings(p,levR) if c>22]
            if not cr: continue
            re=460+cr[0]
            # left edge: background on left differs (arm/tripod). use strongest gradient in cols 465..474
            d=np.diff(p[4:16]); k=np.argmax(d); le=460+4+k+0.5
            W.append(re-le); LE.append(le); RE.append(re)
    W=np.array(W); print(name,'n=%d  width median %.2f  IQR %.2f-%.2f   LE med %.2f  RE med %.2f'%(len(W),np.median(W),*np.percentile(W,[25,75]),np.median(LE),np.median(RE)))
