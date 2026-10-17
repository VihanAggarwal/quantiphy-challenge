import cv2,numpy as np,sys
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
v=sys.argv[1]
img=cv2.imread(f'{W}/{v}_medA.png'); g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(float)
front=[]
for x in range(726,806,2):
    yc=381.6+0.046*(x-730)
    y0=int(round(yc-3)); p=g[y0:y0+7,x]; i=int(np.argmin(p))
    if 0<i<len(p)-1:
        den=(p[i-1]-2*p[i]+p[i+1]); d=(p[i-1]-p[i+1])/(2*den) if den!=0 else 0
        front.append((x,y0+i+d))
P=np.array(front); A=np.c_[P[:,0],np.ones(len(P))]
for it in range(3):
    k,b=np.linalg.lstsq(A,P[:,1],rcond=None)[0]; r=P[:,1]-A@[k,b]; keep=np.abs(r)<max(0.7,2.5*r.std()); P=P[keep]; A=A[keep]
print(v,'front dark line y=%.4f x + %.2f, sd %.2f n %d'%(k,b,r.std(),len(P)))
E=np.load(f'{W}/{v}_bookedges.npy'); E[2]=[k,b]; np.save(f'{W}/{v}_bookedges.npy',E)
kl,bl=E[1]; y=(k*bl+b)/(1-k*kl); print('FL corner (left edge ∩ front line)',round(kl*y+bl,2),round(y,2))
