import cv2,sys
vid=sys.argv[1]; f=int(sys.argv[2]); x0,y0,x1,y1=[int(v) for v in sys.argv[3].split(',')]; out=sys.argv[4]; sc=float(sys.argv[5]) if len(sys.argv)>5 else 1.0
grid=int(sys.argv[6]) if len(sys.argv)>6 else 50
cap=cv2.VideoCapture(vid); cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
c=im[y0:y1,x0:x1].copy()
for x in range((x0//grid+1)*grid,x1,grid):
    cv2.line(c,(x-x0,0),(x-x0,8 if x%(grid*2) else 16),(0,255,0),1)
    if x%(grid*4)==0: cv2.putText(c,str(x),(x-x0+2,28),0,0.45,(0,255,0),1)
for y in range((y0//grid+1)*grid,y1,grid):
    cv2.line(c,(0,y-y0),(8 if y%(grid*2) else 16,y-y0),(0,255,0),1)
    if y%(grid*4)==0: cv2.putText(c,str(y),(18,y-y0+4),0,0.45,(0,255,0),1)
c=cv2.resize(c,None,fx=sc,fy=sc)
cv2.imwrite(out,c)
