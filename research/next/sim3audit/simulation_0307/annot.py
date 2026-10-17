import cv2,numpy as np,sys
k=sys.argv[1]; ref=24
R=np.load('recon.npy',allow_pickle=True).item()
P=np.load(f'P3_{k}.npy'); T=R[k]['T']
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{k}.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,ref); ok,f=cap.read()
x0,y0=950,500; cr=f[y0:760,x0:1600].copy(); s=2
cr=cv2.resize(cr,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
fo=P[:,0]-np.median(P[:,0])
for j in range(len(T)):
    x,y=T[j,ref]; p=(int((x-x0)*s),int((y-y0)*s))
    t=(fo[j]-fo.min())/(fo.max()-fo.min())
    col=(int(255*(1-t)),0,int(255*t))  # blue=rear, red=front
    cv2.circle(cr,p,5,col,-1)
    cv2.putText(cr,f'{fo[j]:.1f}',(p[0]+5,p[1]-4),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,255,255),1)
cv2.imwrite(f'frames/annot_{k}.png',cr)
