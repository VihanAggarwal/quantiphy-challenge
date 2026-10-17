import cv2,sys,numpy as np
# usage: gridcrop.py video frame x0,y0,x1,y1 scale step out
v=sys.argv[1]; fi=int(sys.argv[2]); x0,y0,x1,y1=[int(t) for t in sys.argv[3].split(',')]
sc=float(sys.argv[4]); step=int(sys.argv[5]); out=sys.argv[6]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES,fi)
i=0
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
while True:
    ok,f=c.read()
    if i==fi: break
    i+=1
g=cv2.resize(f[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST if sc>=4 else cv2.INTER_CUBIC)
for x in range((x0//step+1)*step, x1, step):
    X=int((x-x0)*sc); cv2.line(g,(X,0),(X,g.shape[0]),(0,0,255) if x%(step*5)==0 else (0,200,255),1)
    if x%(step*5)==0: cv2.putText(g,str(x),(X+2,12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
for y in range((y0//step+1)*step, y1, step):
    Y=int((y-y0)*sc); cv2.line(g,(0,Y),(g.shape[1],Y),(0,0,255) if y%(step*5)==0 else (0,200,255),1)
    if y%(step*5)==0: cv2.putText(g,str(y),(2,Y-2),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
cv2.imwrite(out,g)
