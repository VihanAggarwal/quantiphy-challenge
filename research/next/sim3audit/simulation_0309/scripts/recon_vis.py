import numpy as np, cv2
d=np.load('joint0302.npz'); T=d['T']; t=d['t']; vp=d['vp']; s=d['s']
c=np.array([1280.,720.]); w=vp-c; f=3556.
Vh=np.array([w[0],w[1],f]); Vh/=np.linalg.norm(Vh); Vz=1.29*Vh[2]
Z=Vz*(t[0]-s)
X=np.stack([Z*(T[0,:,0]-c[0])/f, Z*(T[0,:,1]-c[1])/f, Z],1)
a=X@Vh
# lateral axes: up-ish = component of camera -y orthogonal to V; side = V x up
up=np.array([0,-1.,0]); up-= (up@Vh)*Vh; up/=np.linalg.norm(up); side=np.cross(Vh,up)
b=X@side; h=X@up
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0302.mp4')
for i in range(52): ok,fr=cap.read()
fr=fr.copy()
amax=a.max()
for j in range(T.shape[1]):
    x,y=T[0,j]
    cv2.circle(fr,(int(x),int(y)),3,(0,0,255),-1)
    if j%4==0: cv2.putText(fr,f'{a[j]-amax:.2f}',(int(x)+4,int(y)-2),cv2.FONT_HERSHEY_SIMPLEX,0.42,(0,0,0),1)
cv2.imwrite('frames/along0302_051.png',fr[180:640,640:1500])
np.savez('recon0302.npz',X=X,a=a,b=b,h=h,Vh=Vh,f=f)
# body-axis points: those within the central region (exclude wings): lateral |b - b_head|<0.12
