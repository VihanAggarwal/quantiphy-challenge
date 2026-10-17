# Table-top edges from the x-render median: subpixel boundary points, line fits, corners
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
med=cv2.imread(D+'img/median_x.png').astype(float)
g=cv2.GaussianBlur(med.max(axis=2),(3,3),0)
def sub_edge(prof):
    # subpixel location of the max gradient magnitude along a profile
    d=np.diff(prof); k=np.argmax(np.abs(d))
    if 0<k<len(d)-1:
        a,b,c=np.abs(d[k-1:k+2]); off=0.5*(a-c)/(a-2*b+c)
    else: off=0
    return k+0.5+off
def fitline(xs,ys,tol=1.0):
    xs=np.array(xs);ys=np.array(ys); p=np.polyfit(xs,ys,1)
    for _ in range(3):
        keep=np.abs(ys-np.polyval(p,xs))<tol; p=np.polyfit(xs[keep],ys[keep],1)
    return p, np.std(ys[keep]-np.polyval(p,xs[keep])), keep.mean()
# back edge: vertical profiles rows 405..445, exclude ball columns
bx,by=[],[]
for x in range(590,840):
    if 630<=x<=668 or 752<=x<=800: continue
    bx.append(x); by.append(405+sub_edge(g[405:445,x]))
pb,sb,kb=fitline(bx,by); print('back y=%.5f x+%.2f  sd %.2f keep %.2f'%(pb[0],pb[1],sb,kb))
# left side: horizontal profiles; right side
lx,ly,rx,ry=[],[],[],[]
for y in range(432,478):
    xl=np.where(g[y,380:720]>40)[0]
    if len(xl): x0=380+xl[0]; lx.append(x0-6+sub_edge(g[y,x0-6:x0+6])); ly.append(y)
for y in range(434,488):
    xr=np.where(g[y,720:1100]>40)[0]
    if len(xr): x1=720+xr[-1]; rx.append(x1-6+sub_edge(g[y,x1-6:x1+7])); ry.append(y)
pl,sl,kl=fitline(ly,lx); pr,sr,kr=fitline(ry,rx)
print('left x=%.4f y+%.2f sd %.2f keep %.2f'%(pl[0],pl[1],sl,kl)); print('right x=%.4f y+%.2f sd %.2f keep %.2f'%(pr[0],pr[1],sr,kr))
# front edge: top surface -> front face transition (strongest negative/positive grad in gray)
gray=cv2.GaussianBlur(cv2.cvtColor(med.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(float),(3,3),0)
fx,fy=[],[]
for x in range(495,935):
    prof=gray[470:505,x]; d=np.diff(prof); k=np.argmin(d)
    if 0<k<len(d)-1:
        a,b,c=d[k-1:k+2]; off=0.5*(a-c)/(a-2*b+c)
    else: off=0
    fx.append(x); fy.append(470+k+0.5+off)
pf,sf,kf=fitline(fx,fy,1.5); print('front y=%.5f x+%.2f sd %.2f keep %.2f'%(pf[0],pf[1],sf,kf))
def X(py,px):
    x=(px[0]*py[1]+px[1])/(1-px[0]*py[0]); return np.array([x,py[0]*x+py[1]])
C=dict(BL=X(pb,pl),BR=X(pb,pr),FL=X(pf,pl),FR=X(pf,pr))
for k,v in C.items(): print(k,v.round(2))
json.dump({k:v.tolist() for k,v in C.items()},open(D+'corners.json','w'))
# overlay
im=cv2.imread(D+'img/median_x.png')
for a,b in [('BL','BR'),('BR','FR'),('FR','FL'),('FL','BL')]:
    cv2.line(im,tuple(int(round(v)) for v in C[a]),tuple(int(round(v)) for v in C[b]),(0,0,255),1)
cv2.imwrite(D+'img/corners_overlay.png',cv2.resize(im[400:520,430:1000],None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST))
