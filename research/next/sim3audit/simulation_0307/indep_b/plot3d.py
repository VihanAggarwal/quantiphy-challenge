import numpy as np, cv2, sys
from frame3d import axes
f=3575
V,S,U=axes(f)
imgs=[]
for c in sys.argv[1:]:
    D=np.load(f'dense3d_{c}.npy')
    X=D[:,:3]
    # reference: fin-top midpoint from sweep (approx) -> use fixed ref point
    ref=np.array([0.0,0.0,0.0])
    loc=np.c_[X@V,X@S,X@U]
    ref=np.median(loc,0)
    loc-=ref
    sc=25; W=1100;H=700
    img=np.full((H,W,3),255,np.uint8)
    o1=(260,350); o2=(800,350)
    for k in range(-14,15,2):
        cv2.line(img,(o1[0]+k*sc,0),(o1[0]+k*sc,H),(225,225,225),1)
        cv2.line(img,(0,o1[1]-k*sc),(540,o1[1]-k*sc),(225,225,225),1)
        cv2.line(img,(o2[0]+k*sc,0),(o2[0]+k*sc,H),(225,225,225),1)
    cv2.line(img,(o1[0],0),(o1[0],H),(150,150,150),1); cv2.line(img,(0,o1[1]),(540,o1[1]),(150,150,150),1)
    cv2.line(img,(o2[0],0),(o2[0],H),(150,150,150),1); cv2.line(img,(540,o2[1]),(W,o2[1]),(150,150,150),1)
    for l in loc:
        img[np.clip(int(o1[1]-l[0]*sc),0,H-1),np.clip(int(o1[0]+l[1]*sc),0,W-1)]=(0,0,200)
        x=int(o2[0]+l[0]*sc); y=int(o2[1]-l[2]*sc)
        if 540<x<W and 0<y<H: img[y,x]=(200,0,0)
    cv2.putText(img,c+' top: x=span(R+), y=fore(up)  grid 2m',(10,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1)
    cv2.putText(img,'side: x=fore(right=front), y=up',(560,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1)
    imgs.append(img)
    print(c,'ref',ref,'fore pct',np.percentile(loc[:,0],[0.5,1,99,99.5]),'span pct',np.percentile(loc[:,1],[0.5,99.5]))
cv2.imwrite('fr/dense_top.png',np.vstack(imgs))
