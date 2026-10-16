import cv2, numpy as np, sys
# fine-grid crop: tag frame x0 y0 x1 y1 scale out [step]
tag=sys.argv[1]; fr=int(sys.argv[2]); x0,y0,x1,y1=map(int,sys.argv[3:7]); sc=float(sys.argv[7]); out=sys.argv[8]
step=int(sys.argv[9]) if len(sys.argv)>9 else 10
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
im=cv2.imread(D+(f'frames/{tag}{fr:02d}.png' if fr>=0 else f'frames/{tag}.png'))[y0:y1,x0:x1]
im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
for gx in range((x0//step+1)*step,x1,step):
    X=int((gx-x0)*sc); c=(0,0,255) if gx%50==0 else (0,160,0)
    cv2.line(im,(X,0),(X,im.shape[0]),c,1)
    if gx%50==0: cv2.putText(im,str(gx),(X+2,12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
for gy in range((y0//step+1)*step,y1,step):
    Y=int((gy-y0)*sc); c=(0,0,255) if gy%50==0 else (0,160,0)
    cv2.line(im,(0,Y),(im.shape[1],Y),c,1)
    if gy%50==0: cv2.putText(im,str(gy),(2,Y-2),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
cv2.imwrite(D+out,im)
