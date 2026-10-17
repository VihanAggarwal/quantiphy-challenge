"""Sub-pixel horizontal half-max width of the ball (s render, redness R-G), per video frame.
Also the vertical half-max extent and the X-render rim width for cross-check."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/track.json'))
def cross(p, lev):
    # first/last crossing of level in 1D profile p (sub-pixel)
    idx=np.nonzero(p>=lev)[0]
    if len(idx)==0: return None
    i0,i1=idx[0],idx[-1]
    l=i0-1+(lev-p[i0-1])/(p[i0]-p[i0-1]) if i0>0 else i0
    r=i1+(p[i1]-lev)/(p[i1]-p[i1+1]) if i1+1<len(p) else i1
    return l,r
res=[]
fr=frames('s')
for i,im in enumerate(fr):
    u,v=T['s'][i]['u'],T['s'][i]['v']
    x0,y0=int(u)-40,int(v)-40
    c=im[y0:y0+80,x0:x0+80].astype(float)
    red=c[:,:,2]-c[:,:,1]           # R-G
    bg=np.median(np.r_[red[:,:6].ravel(),red[:,-6:].ravel()])
    core=np.percentile(red[30:50,30:50],50)
    lev=bg+0.5*(core-bg)
    ws=[]
    for y in range(80):
        p=cv2.GaussianBlur(red[y:y+1,:],(1,1),0)[0] if False else red[y]
        cr=cross(p,lev)
        if cr: ws.append((cr[1]-cr[0],y,(cr[0]+cr[1])/2))
    ws.sort(reverse=True)
    wtop=np.median([w for w,_,_ in ws[:5]])
    # vertical extent: columns near centre
    hs=[]
    for x in range(30,50):
        cr=cross(red[:,x],lev)
        if cr: hs.append(cr[1]-cr[0])
    hs.sort(reverse=True)
    res.append(dict(f=i,wh=float(wtop),hv=float(np.median(hs[:5])),bg=float(bg),core=float(core)))
json.dump(res,open('/home/user/quantiphy-challenge/research/next/labaudit2/0010/size_s.json','w'))
for r in res: print(f"{r['f']:2d} c{cap(r['f']):2d} wh={r['wh']:5.2f} hv={r['hv']:5.2f}  Rc(wh)={F*0.07/r['wh']:.3f}  bg={r['bg']:.0f} core={r['core']:.0f}")
