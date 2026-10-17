import cv2, numpy as np, sys
P='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0044.mp4'
out=sys.argv[1]
c=cv2.VideoCapture(P); fr=[]; i=0
while True:
    ok,im=c.read()
    if not ok: break
    if i>=150 and i%5==0: fr.append(im)
    i+=1
bg=np.median(np.array(fr),axis=0).astype(np.uint8)
def crop(x0,y0,w,h,S,step=10):
    cr=cv2.resize(bg[y0:y0+h,x0:x0+w],(w*S,h*S),interpolation=cv2.INTER_CUBIC)
    for yy in range(0,h,5):
        L=6 if yy%10 else (14 if yy%50 else 24)
        cv2.line(cr,(0,yy*S),(L,yy*S),(0,0,255),1)
        if yy%step==0: cv2.putText(cr,str(y0+yy),(26,yy*S+5),0,0.4,(0,0,255),1)
    for xx in range(0,w,5):
        L=6 if xx%10 else (14 if xx%50 else 24)
        cv2.line(cr,(xx*S,0),(xx*S,L),(255,0,0),1)
        if xx%50==0: cv2.putText(cr,str(x0+xx),(xx*S+2,38),0,0.4,(255,0,0),1)
    return cr
# tops (2x): plastic bottle, green bottle, cylinder, kettle
tops=[crop(570,400,110,70,2),crop(790,280,110,70,2),crop(960,580,140,70,2),crop(1150,500,180,70,2)]
cv2.imwrite(out+'/t44.png',np.hstack(tops))
bots=[crop(100,760,140,70,2),crop(560,760,140,70,2),crop(760,760,140,70,2),crop(960,760,140,70,2),crop(1300,760,140,70,2)]
cv2.imwrite(out+'/b44.png',np.hstack(bots))
cv2.imwrite(out+'/bowl44.png',crop(100,620,420,200,1,step=50))
cv2.imwrite(out+'/full44.png',np.hstack([crop(540,260,170,560,1,step=20),crop(760,260,170,560,1,step=20),crop(950,260,170,560,1,step=20),crop(1140,260,380,560,1,step=20)]))
