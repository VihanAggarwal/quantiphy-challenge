# Per-frame white-ball top edge (half-max vs local background above) and bottom (darkest row of the
# contact shadow / mask gap below the ball), median over the central columns; plus equator-row left/right edges.
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
T=json.load(open(D+'track.json'))
def subcross(p,lvl,i,j):
    a,b=p[i],p[j]; return i+(j-i)*(a-lvl)/(a-b) if a!=b else i
res={}
for r in ['x','o']:
    fr=frames('' if r=='o' else r); res[r]={}
    for k in range(32,49):
        V=fr[k].max(axis=2).astype(float)
        t=T['x'][str(k)]['wht']; cx=int(round(t['cx'])); cy=int(round(t['cy']))
        tops=[];bots=[]
        for x in range(cx-3,cx+4):
            p=V[cy-22:cy+26,x]; c=22
            pk=np.max(p[c-6:c+3])
            # top: walk up from the brightest row above centre
            i=c-6+np.argmax(p[c-6:c+3])
            bg=np.median(p[0:4]); lvl=(pk+bg)/2
            while i>0 and p[i-1]>=lvl: i-=1
            tops.append(cy-22+subcross(p,lvl,i,i-1))
            # bottom: darkest row in the window cy+4..cy+20 (contact shadow / mask gap), parabolic refine
            seg=p[c+4:c+22]; j=np.argmin(seg)
            if 0<j<len(seg)-1:
                a,b,cc=seg[j-1:j+2]; off=0.5*(a-cc)/(a-2*b+cc) if (a-2*b+cc)!=0 else 0
            else: off=0
            bots.append(cy+4+j+off)
        yt=np.median(tops); yb=np.median(bots)
        ym=int(round((yt+yb)/2)); L=[];R=[]
        for y in range(ym-2,ym+3):
            p=V[y,cx-24:cx+25]; c=24; pk=np.max(p[c-5:c+6]); 
            bl=np.median(p[:4]); br=np.median(p[-4:])
            i=c-5+np.argmax(p[c-5:c+6]); j=i
            ll=(pk+bl)/2; rl=(pk+br)/2
            while i>0 and p[i-1]>=ll: i-=1
            while j<len(p)-1 and p[j+1]>=rl: j+=1
            L.append(cx-24+subcross(p,ll,i,i-1)); R.append(cx-24+subcross(p,rl,j,j+1))
        res[r][k]=dict(top=yt,bot=yb,left=float(np.median(L)),right=float(np.median(R)),topsd=float(np.std(tops)),botsd=float(np.std(bots)))
json.dump(res,open(D+'topbot.json','w'))
print(' k  c |   x: top    bot    h    left  right  w    ux   |  o: top    bot    h    left  right  w   ux')
for k in range(32,49):
    s='%2d %2d |'%(k,cap(k))
    for r in ['x','o']:
        q=res[r][k]; s+=' %6.1f %6.1f %4.1f %6.1f %6.1f %4.1f %6.1f |'%(q['top'],q['bot'],q['bot']-q['top'],q['left'],q['right'],q['right']-q['left'],(q['left']+q['right'])/2)
    print(s)
