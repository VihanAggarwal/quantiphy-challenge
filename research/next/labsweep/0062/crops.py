import cv2,sys
v=sys.argv[1]; fr=int(sys.argv[2]); x0,y0,x1,y1=[int(a) for a in sys.argv[3].split(',')]; s=float(sys.argv[4]); out=sys.argv[5]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_{v}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES,0)
for i in range(fr+1): ok,f=c.read()
cr=f[y0:y1,x0:x1]; cr=cv2.resize(cr,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
# grid ticks every 20 px in source coords
for x in range(x0 - x0%20 + 20, x1, 20):
    X=int((x-x0)*s); cv2.line(cr,(X,0),(X,6 if x%100 else 14),(0,0,255),1)
for y in range(y0 - y0%20 + 20, y1, 20):
    Y=int((y-y0)*s); cv2.line(cr,(0,Y),(6 if y%100 else 14,Y),(0,0,255),1)
cv2.imwrite(out,cr)
