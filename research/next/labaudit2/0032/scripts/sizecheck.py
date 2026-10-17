# Equator half-max width and top edge for both balls vs the plane-route depth (size route consistency check)
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
T=json.load(open(D+'track.json'))
YH=349.7
def subcross(p,lvl,i,j):
    a,b=p[i],p[j]; return i+(j-i)*(a-lvl)/(a-b) if a!=b else i
def chan(im,key):
    if key=='wht': return im.max(axis=2).astype(float)
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); return hsv[...,1].astype(float)   # yellow: saturation
def widths(V,cx,cy,W=40):
    # find equator row = row of max half-max width near cy
    best=None
    for y in range(cy-6,cy+7):
        p=V[y,cx-W:cx+W+1]; c=W; pk=np.percentile(p[c-6:c+7],70); bl=np.median(p[:4]); br=np.median(p[-4:])
        i=c; j=c; ll=(pk+bl)/2; rl=(pk+br)/2
        if p[c]<ll: continue
        while i>0 and p[i-1]>=ll: i-=1
        while j<len(p)-1 and p[j+1]>=rl: j+=1
        l=subcross(p,ll,i,i-1); r=subcross(p,rl,j,j+1)
        if best is None or r-l>best[0]: best=(r-l,y,cx-W+(l+r)/2)
    return best
def top(V,cx,cy,R):
    ts=[]
    for x in range(cx-2,cx+3):
        p=V[cy-R-10:cy+1,x]; pk=np.percentile(p[-6:],70); bg=np.median(p[:4]); lvl=(pk+bg)/2
        i=len(p)-1
        while i>0 and p[i-1]>=lvl: i-=1
        ts.append(cy-R-10+subcross(p,lvl,i,i-1))
    return np.median(ts)
for r in ['x','o']:
    fr=frames('' if r=='o' else r)
    for key,ks,R in [('yel',range(20,42),20),('wht',range(33,49),11)]:
        print('==',r,key)
        rows=[]
        for k in ks:
            t=T['x'][str(k)][key]; cx=int(round(t['cx'])); cy=int(round(t['cy']))
            V=chan(fr[k],key)
            w=widths(V,cx,cy,W=R*2); yt=top(V,cx,cy,R)
            rows.append((k,w[0],w[1],yt))
        k0=rows[0]
        for k,w,ye,yt in rows:
            print('  v%2d c%2d  w %5.1f  eqrow %d  top %6.1f   w*(top-yh) %7.1f   w*(eq-yh) %7.1f'%(k,cap(k),w,ye,yt,w*(yt-YH),w*(ye-YH)))
