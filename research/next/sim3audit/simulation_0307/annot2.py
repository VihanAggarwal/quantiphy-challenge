import cv2,numpy as np,sys
k=sys.argv[1]; ref=int(sys.argv[2])
R=np.load('recon.npy',allow_pickle=True).item()
P=np.load(f'P3_{k}.npy'); T=R[k]['T']
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{k}.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,ref); ok,f=cap.read()
x0,y0,x1,y1=1320,690,2020,1010
cr=f[y0:y1,x0:x1].copy(); s=1.8
cr=cv2.resize(cr,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
allp=np.concatenate([np.load(f'P3_{kk}.npy') for kk in ['0303','0305','0307']])
fm=np.median(allp[:,0]); lm=np.median(allp[:,1])+0.65
for j in range(len(T)):
    x,y=T[j,ref]; p=(int((x-x0)*s),int((y-y0)*s))
    cv2.circle(cr,p,4,(0,0,255),-1)
    cv2.putText(cr,f'{P[j,0]-fm:.1f}/{P[j,1]-lm:.1f}',(p[0]+4,p[1]-3),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1)
cv2.imwrite(f'frames/annot2_{k}_{ref}.png',cr)
