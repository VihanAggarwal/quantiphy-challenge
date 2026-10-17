# Fit the typewriter base-plate bottom outline (front edge, left edge) in a glass-take frame, then yaw + footprint.
import cv2, numpy as np, sys
from a3cam import *
from tw_yaw import yaw_of_line
vid=sys.argv[1]; fi=int(sys.argv[2])
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
for i in range(fi+1): ok,im=cap.read()
Y=cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32),(3,3),0)
gy=np.diff(Y,axis=0)  # + when getting brighter downward (base dark -> desk lighter)
gx=np.diff(Y,axis=1)
fp=[]
for x in range(955,1135,3):
    col=gy[712:775,x]; k=np.argmax(col)
    if col[k]>6: fp.append((x,712+k+0.5))
fp=np.array(fp)
lp=[]
for y in range(706,752,2):
    row=gx[y,840:935]; k=np.argmin(row)   # desk (lighter) on left -> base dark on right: negative gradient
    if row[k]<-6: lp.append((840+k+0.5,y))
lp=np.array(lp)
def rline(P,xy=True):
    a=P[:,0] if xy else P[:,1]; b=P[:,1] if xy else P[:,0]; m=np.ones(len(a),bool)
    for it in range(4):
        p=np.polyfit(a[m],b[m],1); r=b-np.polyval(p,a); s=np.std(r[m]); m=np.abs(r)<max(0.8,2.5*s)
    return p,np.std(r[m]),m.sum()
pf,sf,nf=rline(fp,True)     # y = pf(x)
pl,sl,nl=rline(lp,False)    # x = pl(y)
print('front edge y=%.4f x + %.1f rms %.2f n=%d'%(pf[0],pf[1],sf,nf),' left edge x=%.4f y + %.1f rms %.2f n=%d'%(pl[0],pl[1],sl,nl))
# corner = intersection
# x = pl0*y+pl1 ; y = pf0*x+pf1
y=(pf[0]*pl[1]+pf[1])/(1-pf[0]*pl[0]); x=pl[0]*y+pl[1]
print('front-left corner (%.1f,%.1f)'%(x,y))
for f in (2630.,2650.,2670.):
    th,M=setup(f)
    hN=-3.593*ray(*N,f,M)[2]; hR=-5.009*ray(*R,f,M)[2]; h=(hN+hR)/2
    P={k:onplane(*p,f,M,h) for k,p in dict(N=N,R=R,L=L,F=F).items()}
    ex=(P['R']-P['N'])/np.linalg.norm(P['R']-P['N']); ey=(P['L']-P['N'])/np.linalg.norm(P['L']-P['N'])
    yf=yaw_of_line((960,np.polyval(pf,960)),(1130,np.polyval(pf,1130)),f,M,ex,ey)
    yl=yaw_of_line((np.polyval(pl,706),706),(np.polyval(pl,750),750),f,M,ex,ey)
    print('  f=%.0f yaw front edge %.2f deg, left edge %.2f deg (90 = parallel to desk short axis)'%(f,yf,yl))
