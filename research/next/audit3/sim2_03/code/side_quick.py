import cv2, numpy as np, sys, json
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
def frames(v):
    c=cv2.VideoCapture(D+v+'.mp4')
    while True:
        ok,f=c.read()
        if not ok: break
        yield f
def edge_sub(prof, thr):
    # subpixel first/last crossing of 1D profile above thr
    idx=np.where(prof>thr)[0]
    if len(idx)==0: return None,None
    a,b=idx[0],idx[-1]
    # interpolate
    def interp(i0,i1):
        p0,p1=prof[i0],prof[i1]
        return i0+(thr-p0)/(p1-p0)*(i1-i0) if p1!=p0 else i0
    L=interp(a-1,a) if a>0 else a
    R=interp(b,b+1) if b<len(prof)-1 else b
    return L,R
res={}
for v in sys.argv[1:]:
    rows=[]
    for k,f in enumerate(frames(v)):
        g=f.astype(np.int16)
        dist=np.abs(255-g).sum(2)  # distance from white
        m=dist>60
        boat=m[:690]; shark=m[690:]
        bc=boat.sum(0); sc=shark.sum(0); sr=shark.sum(1)
        bx=np.where(bc>0)[0]; sx=np.where(sc>0)[0]; sy=np.where(sr>0)[0]
        # boat: count columns; shark: extents
        r=dict(k=k)
        if len(bx): r.update(bL=int(bx[0]),bR=int(bx[-1]))
        if len(sx):
            r.update(sL=int(sx[0]),sR=int(sx[-1]),sT=int(sy[0])+690,sB=int(sy[-1])+690)
            ys,xs=np.nonzero(shark); r.update(scx=float(xs.mean()),scy=float(ys.mean())+690)
        rows.append(r)
    res[v]=rows
    print(v, len(rows))
    for r in rows[::6]: print('  ',r)
json.dump(res,open('/home/user/quantiphy-challenge/research/next/audit3/sim2_03/code/side_quick_%s.json'%sys.argv[1],'w'))
