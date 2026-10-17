import cv2, numpy as np, sys
sys.path.insert(0,'scripts')
from cam import *
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0212.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
B=np.load('dogbox.npy')
c0=3.73
# frame-to-frame template tracking of the back/flank band (rows 660-760), template = central part of dog bbox
xs=[]; 
u=None
pos=[]
for i in range(len(F)-1):
    x0,x1=B[i,1],B[i,2]
    if i==0: u=(x0+x1)/2
    # template around current u, width 160, rows 665-745 (upper torso, above legs)
    tw=80
    T=F[i][665:745, int(u-tw):int(u+tw)]
    S=F[i+1][665:745, int(u-tw-60):int(u+tw+20)]
    r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
    k=np.argmax(r[0]); 
    # subpixel
    if 0<k<r.shape[1]-1:
        y0,y1,y2=r[0,k-1],r[0,k],r[0,k+1]; dk=0.5*(y0-y2)/(y0-2*y1+y2)
    else: dk=0
    du=(k+dk)-60
    pos.append(u); u=u+du
pos.append(u)
pos=np.array(pos); t=np.arange(len(pos))/24
A=a_from_u(pos,c0)
np.save('dog_torso_u.npy',pos)
for i in range(0,len(pos),3): print('f%02d u=%.1f a=%.3f'%(i,pos[i],A[i]))
# speed: backward differences smoothed
for tt in [0.5,1.0,1.5,1.75]:
    i=int(round(tt*24))
    for w in [3,4,6]:
        v=(A[i-w]-A[i+w])/(2*w/24)  # central over +-w frames
        print('t=%.2f central +-%d frames speed=%.3f'%(tt,w,v))
# local quadratic fits
for tt in [1.0,1.5]:
    i=int(round(tt*24))
    for w in [5,8]:
        sl=slice(i-w,i+w+1); p=np.polyfit(t[sl],A[sl],2)
        print('t=%.1f quad fit +-%d: v=%.3f'%(tt,w,-np.polyval(np.polyder(p),tt)))
