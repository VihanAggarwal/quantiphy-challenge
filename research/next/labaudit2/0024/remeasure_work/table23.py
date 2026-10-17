import cv2,numpy as np
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
img=cv2.imread(f'{W}/captured_0023x_medB.png')
m=(img.max(axis=2)>35).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
def fitP(P,vert=False):
    P=np.array(P,float)
    for it in range(3):
        A=np.c_[P[:,1] if vert else P[:,0],np.ones(len(P))]; yv=P[:,0] if vert else P[:,1]
        k,b=np.linalg.lstsq(A,yv,rcond=None)[0]; r=yv-A@[k,b]; keep=np.abs(r)<max(0.8,2.5*r.std()); P=P[keep]
    return k,b,r.std(),len(P)
# left side edge: leftmost table pixel for rows 450..525
left=[(np.where(m[y,200:640])[0].min()+200,y) for y in range(452,526)]
right=[(np.where(m[y,640:1100])[0].max()+640,y) for y in range(452,522)]
far=[(x,np.where(m[400:520,x])[0].min()+400) for x in list(range(445,490))+list(range(690,760))]
print('left',fitP(left,True)); print('right',fitP(right,True)); print('far',fitP(far))
kl,bl,_,_=fitP(left,True); kr,br,_,_=fitP(right,True); kf,bf,_,_=fitP(far)
# VP of side edges: x = k y + b
y=(br-bl)/(kl-kr); x=kl*y+bl; print('VP sides',x,y)
# far corners
def ixv(kh,bh,kv,bv): yy=(kh*bv+bh)/(1-kh*kv); return kv*yy+bv,yy
print('far-left corner',ixv(kf,bf,kl,bl),'far-right',ixv(kf,bf,kr,br))
for x in [300,450,640,800,900]:
    col=img[500:570,x].astype(int).sum(1); 
    print('col',x,' '.join('%d'%c for c in col[::2]))
