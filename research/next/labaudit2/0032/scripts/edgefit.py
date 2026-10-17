# White-ball half-max edges: centre (edge midpoints) and vertical/horizontal extents, per render & frame
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
T=json.load(open(D+'track.json'))
def cross(prof, lvl, start, step):
    # walk from start in direction step until prof < lvl; return subpixel crossing
    i=start
    while 0<=i+step<len(prof) and prof[i+step]>=lvl: i+=step
    j=i+step
    if not (0<=j<len(prof)): return np.nan
    a,b=prof[i],prof[j]; return i+step*(a-lvl)/(a-b)
def measure(img, cx, cy, half=4, R=22):
    V=cv2.GaussianBlur(img.max(axis=2).astype(float),(3,3),0.7)
    cx_i,cy_i=int(round(cx)),int(round(cy))
    tops,bots,lefts,rights=[],[],[],[]
    for dx in range(-half,half+1):
        x=cx_i+dx; prof=V[cy_i-R:cy_i+R+1,x]; c=R
        pk=np.percentile(prof[c-4:c+5],80)
        bt=np.median(prof[max(0,c-R):max(1,c-R+4)]); bb=np.median(prof[-4:])
        t=cross(prof,(pk+bt)/2,c,-1); b=cross(prof,(pk+bb)/2,c,+1)
        tops.append(cy_i-R+t); bots.append(cy_i-R+b)
    for dy in range(-half,half+1):
        y=cy_i+dy; prof=V[y,cx_i-R:cx_i+R+1]; c=R
        pk=np.percentile(prof[c-4:c+5],80)
        bl=np.median(prof[:4]); br=np.median(prof[-4:])
        l=cross(prof,(pk+bl)/2,c,-1); r=cross(prof,(pk+br)/2,c,+1)
        lefts.append(cx_i-R+l); rights.append(cx_i-R+r)
    t,b,l,r=[np.nanmedian(a) for a in (tops,bots,lefts,rights)]
    return dict(top=t,bot=b,left=l,right=r,ux=(l+r)/2,uy=(t+b)/2,h=b-t,w=r-l)
out={}
for r in ['x','o','s']:
    fr=frames('' if r=='o' else r); out[r]={}
    for k in range(32,49):
        tr=T['x'][str(k)]['wht']  # x-render centroid as seed (shared geometry)
        m=measure(fr[k],tr['cx'],tr['cy'])
        m2=measure(fr[k],m['ux'],m['uy'])
        out[r][k]=m2
json.dump(out,open(D+'edges_white.json','w'))
print(' k  c  | '+' | '.join('%s: ux     uy     w     h  '%r for r in ['x','o','s']))
for k in range(32,49):
    print('%2d %2d | '%(k,cap(k))+' | '.join('%6.1f %6.1f %5.1f %5.1f'%(out[r][k]['ux'],out[r][k]['uy'],out[r][k]['w'],out[r][k]['h']) for r in ['x','o','s']))
