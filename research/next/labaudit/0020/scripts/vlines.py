import cv2, numpy as np
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
med=cv2.imread(d+'median_o.png')
g=cv2.cvtColor(med,cv2.COLOR_BGR2GRAY).astype(float)
g=cv2.GaussianBlur(g,(3,3),0)
gx=cv2.Sobel(g,cv2.CV_64F,1,0,ksize=5)
def trace(x0,x1,ys,sign):
    pts=[]
    for y in ys:
        row=gx[y,x0:x1]*sign
        k=np.argmax(row)
        if row[k]>50: pts.append((x0+k,y))
    P=np.array(pts,float)
    A=np.c_[P[:,1],np.ones(len(P))]; c,res,_,_=np.linalg.lstsq(A,P[:,0],rcond=None)
    r=P[:,0]-A@c
    return c,np.std(r),len(P)
feats={'vent_left':(840,905,range(150,280,2),1),'vent_right':(1025,1075,range(160,290,2),-1),
       'seam1130':(1100,1160,range(10,250,2),-1),'seam1130b':(1100,1160,range(10,250,2),1),
       'seam955':(930,980,range(5,120,2),1),'seam955b':(930,980,range(5,120,2),-1)}
for k,(a,b,ys,s) in feats.items():
    c,sd,n=trace(a,b,ys,s)
    print(k,'x = %.4f*y + %.1f  sd %.2f n %d'%(c[0],c[1],sd,n))
