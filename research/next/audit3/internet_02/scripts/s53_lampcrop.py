import cv2, numpy as np, sys
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0053.mp4'
c=cv2.VideoCapture(P); F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
bg=np.median(np.array(F[::2]),axis=0).astype(np.uint8)
def crop(x0,y0,w,h,S):
    cr=cv2.resize(bg[y0:y0+h,x0:x0+w],(w*S,h*S),interpolation=cv2.INTER_CUBIC)
    for yy in range(0,h,5):
        L=6 if yy%10 else (14 if yy%50 else 30)
        cv2.line(cr,(0,yy*S),(L,yy*S),(0,0,255),1)
        if yy%10==0: cv2.putText(cr,str(y0+yy),(32,yy*S+5),0,0.4,(0,0,255),1)
    return cr
cv2.imwrite(sys.argv[1]+'/o4.png',np.hstack([crop(490,110,100,90,3),crop(490,640,100,90,3)]))
