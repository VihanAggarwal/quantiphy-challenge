import cv2,numpy as np,sys
clip=sys.argv[1]; ref=int(sys.argv[2]); tag=sys.argv[3] if len(sys.argv)>3 else ''
B=np.load(f'B_{clip}{tag}.npy'); T=np.load(f'Tk_{clip}{tag}.npy')
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{clip}.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,ref); ok,f=cap.read()
x0,y0,x1,y1=1320,690,2020,1010
cr=f[y0:y1,x0:x1].copy(); s=1.8
cr=cv2.resize(cr,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
fm=np.median(B[:,0]); lm=np.median(B[:,1])
for j in range(len(T)):
    x,y=T[j,ref]; p=(int((x-x0)*s),int((y-y0)*s))
    cv2.circle(cr,p,4,(0,0,255),-1)
    cv2.putText(cr,f'{B[j,0]-fm:.1f}/{B[j,1]-lm:.1f}',(p[0]+4,p[1]-3),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1)
cv2.imwrite(f'frames/annot3_{clip}{tag}_{ref}.png',cr)
