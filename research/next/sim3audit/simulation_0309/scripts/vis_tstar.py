import cv2, numpy as np
d=np.load('joint0302.npz'); T=d['T']; s=d['s']
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0302.mp4')
for i in range(52): ok,f=c.read()
f=f.copy()
lo,hi=np.percentile(s,[2,98])
for j in range(T.shape[1]):
    x,y=T[0,j]; v=(s[j]-lo)/(hi-lo); v=min(max(v,0),1)
    col=(int(255*(1-v)),0,int(255*v))  # blue = early t* (far), red = late (near)
    cv2.circle(f,(int(x),int(y)),4,col,-1)
    if j%6==0: cv2.putText(f,f'{s[j]:.2f}',(int(x)+5,int(y)),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,0,0),1)
cv2.imwrite('frames/tstar0302_051.png',f[180:640,640:1500])
