# Tennis ball: equator half-max width (yellowness = b*-a*) vs plane-route predicted silhouette width (size/plane consistency)
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
from geo import plane, X_on
from sil import extents
T=json.load(open(D+'track.json'))
n,Ki,_=plane(711.)
def rayu(p): r=Ki@np.array([p[0],p[1],1.]); return r/np.linalg.norm(r)
def subcross(p,lvl,i,j):
    a,b=p[i],p[j]; return i+(j-i)*(a-lvl)/(a-b) if a!=b else i
for rr in ['x','o']:
    fr=frames('' if rr=='o' else rr); rows=[]
    for k in range(22,42):
        lab=cv2.cvtColor(fr[k],cv2.COLOR_BGR2LAB).astype(float); Y=cv2.GaussianBlur(lab[...,2]-lab[...,1],(3,3),0.7)
        t=T['x'][str(k)]['yel']; cx=int(round(t['cx'])); cy=int(round(t['cy']))
        # vertical extent at centre columns: top & bottom half-max
        tops=[];bots=[]
        for x in range(cx-3,cx+4):
            p=Y[cy-40:cy+41,x]; c=40; pk=np.percentile(p[c-8:c+9],70)
            bt=np.median(p[:5]); bb=np.median(p[-5:])
            i=c; j=c
            while i>0 and p[i-1]>=(pk+bt)/2: i-=1
            while j<len(p)-1 and p[j+1]>=(pk+bb)/2: j+=1
            tops.append(cy-40+subcross(p,(pk+bt)/2,i,i-1)); bots.append(cy-40+subcross(p,(pk+bb)/2,j,j+1))
        yt,yb=np.median(tops),np.median(bots); ym=int(round((yt+yb)/2))
        ws=[];us=[]
        for y in range(ym-3,ym+4):
            p=Y[y,cx-50:cx+51]; c=50; pk=np.percentile(p[c-8:c+9],70); bl=np.median(p[:5]); br=np.median(p[-5:])
            i=c;j=c
            while i>0 and p[i-1]>=(pk+bl)/2: i-=1
            while j<len(p)-1 and p[j+1]>=(pk+br)/2: j+=1
            l=subcross(p,(pk+bl)/2,i,i-1); r=subcross(p,(pk+br)/2,j,j+1); ws.append(r-l); us.append(cx-50+(l+r)/2)
        w=np.median(ws); ux=np.median(us)
        rows.append((k,ux,(yt+yb)/2,w,yb-yt))
    # plane route with h anchored so that surface range at v36 = 1.183
    U={k:np.array([ux,uy]) for k,ux,uy,w,h in rows}
    Xu={k:X_on(U[k],n,Ki,1.0) for k in U}; s=(1.183+0.0335)/np.linalg.norm(Xu[36])
    print('render',rr,' (h=%.4f)'%(s+0.0335))
    rat=[]
    for k,ux,uy,w,h in rows:
        R=np.linalg.norm(Xu[k])*s; C=rayu(U[k])*R; wp,hp=extents(C,0.0335)[:2]
        rat.append((cap(k),w/wp,h/hp))
        print('  v%2d c%2d  u=(%.1f,%.1f)  R_plane %.3f  w %.1f pred %.1f ratio %.3f | h %.1f pred %.1f ratio %.3f'%(k,cap(k),ux,uy,R,w,wp,w/wp,h,hp,h/hp))
    rat=np.array(rat); sel=(rat[:,0]>=23)&(rat[:,0]<=43)
    for j,name in [(1,'w'),(2,'h')]:
        p=np.polyfit(rat[sel,0],rat[sel,j],1); print('  %s ratio trend %.4f/frame -> %.1f%% over 12 frames (mean %.3f)'%(name,p[0],100*12*p[0]/rat[sel,j].mean(),rat[sel,j].mean()))
