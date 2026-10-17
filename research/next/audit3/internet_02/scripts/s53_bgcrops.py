import cv2, numpy as np, sys
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0053.mp4'
out=sys.argv[1]
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
        if yy%50==0: cv2.putText(cr,str(y0+yy),(32,yy*S+5),0,0.45,(0,0,255),1)
    for xx in range(0,w,5):
        L=6 if xx%10 else (14 if xx%50 else 30)
        cv2.line(cr,(xx*S,0),(xx*S,L),(255,255,0),1)
        if xx%50==0: cv2.putText(cr,str(x0+xx),(xx*S+2,44),0,0.45,(255,255,0),1)
    return cr
cv2.imwrite(out+'/o1.png',np.hstack([crop(20,540,170,180,2),crop(1040,540,130,180,2),crop(1790,540,110,180,2)]))
cv2.imwrite(out+'/o2.png',crop(1320,520,360,200,2))
lamp=crop(480,100,120,620,1)
cv2.imwrite(out+'/o3.png',lamp)
