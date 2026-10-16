import cv2, sys
img = cv2.imread(sys.argv[1]); x0,y0,x1,y1=[int(v) for v in sys.argv[2].split(',')]; s=float(sys.argv[3])
c = cv2.resize(img[y0:y1,x0:x1],None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
# grid lines every 10 px
step=int(sys.argv[5]) if len(sys.argv)>5 else 10
for y in range(((y0+step-1)//step)*step, y1, step):
    yy=int((y-y0)*s); cv2.line(c,(0,yy),(8,yy),(0,0,255),1); cv2.putText(c,str(y),(10,yy+4),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,255),1)
for x in range(((x0+step-1)//step)*step, x1, step):
    xx=int((x-x0)*s); cv2.line(c,(xx,0),(xx,8),(0,0,255),1)
    if (x//step)%2==0: cv2.putText(c,str(x),(xx-10,20),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,255),1)
cv2.imwrite(sys.argv[4], c)
