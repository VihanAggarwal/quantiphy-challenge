import cv2, numpy as np, sys
from a3cam import *
from tw_yaw import yaw_of_line
vid=sys.argv[1]; fi=int(sys.argv[2])
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
for i in range(fi+1): ok,im=cap.read()
Y=cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0)
fe=lambda x: 756-0.1488*(x-933)       # eyeballed front edge
le=lambda y: 853+(y-705)*1.569        # eyeballed left edge
fp=[]
for x in range(960,1130,2):
    y0=int(fe(x))-8; col=np.diff(Y[y0:y0+17,x]); k=np.argmax(col)
    if 0<k<len(col)-1 and col[k]>4:
        a,b,c=col[k-1],col[k],col[k+1]; off=0.5*(a-c)/(a-2*b+c) if (a-2*b+c)!=0 else 0
        fp.append((x,y0+k+0.5+off))
lp=[]
for y in range(708,750,1):
    x0=int(le(y))-8; row=np.diff(Y[y,x0:x0+17]); k=np.argmin(row)
    if 0<k<len(row)-1 and row[k]<-4:
        a,b,c=row[k-1],row[k],row[k+1]; off=0.5*(a-c)/(a-2*b+c) if (a-2*b+c)!=0 else 0
        lp.append((x0+k+0.5+off,y))
fp=np.array(fp); lp=np.array(lp)
def rfit(a,b):
    m=np.ones(len(a),bool)
    for it in range(4):
        p=np.polyfit(a[m],b[m],1); r=b-np.polyval(p,a); s=np.std(r[m]); m=np.abs(r)<max(0.7,2.5*s)
    return p,np.std(r[m]),m.sum()
pf,sf,nf=rfit(fp[:,0],fp[:,1]); pl,sl,nl=rfit(lp[:,1],lp[:,0])
print(vid,'front edge y=%.4fx+%.1f rms %.2f n=%d/%d | left edge x=%.4fy+%.1f rms %.2f n=%d/%d'%(pf[0],pf[1],sf,nf,len(fp),pl[0],pl[1],sl,nl,len(lp)))
for f in (2630.,2650.,2670.):
    th,M=setup(f)
    hN=-3.593*ray(*N,f,M)[2]; hR=-5.009*ray(*R,f,M)[2]; h=(hN+hR)/2
    P={k:onplane(*p,f,M,h) for k,p in dict(N=N,R=R,L=L,F=F).items()}
    ex=(P['R']-P['N'])/np.linalg.norm(P['R']-P['N']); ey=(P['L']-P['N'])/np.linalg.norm(P['L']-P['N'])
    yf=yaw_of_line((965,np.polyval(pf,965)),(1125,np.polyval(pf,1125)),f,M,ex,ey)
    yl=yaw_of_line((np.polyval(pl,708),708),(np.polyval(pl,748),748),f,M,ex,ey)
    print('  f=%.0f yaw: front edge %.2f deg; left edge %.2f deg (90 = parallel to desk depth axis); corner angle %.1f'%(f,yf,yl,yl-yf))
