import cv2, numpy as np, sys
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
pre=sys.argv[1]; frames=[int(a) for a in sys.argv[2].split(',')]; x0,x1,y0,y1=[int(a) for a in sys.argv[3].split(',')]; sc=int(sys.argv[4]); out=sys.argv[5]
tiles=[]
for i in frames:
    im=cv2.imread(R1+f'{pre}{i:02d}.png')[y0:y1,x0:x1]
    im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    # grid lines every 10 px
    for yy in range(0,y1-y0,10): im[yy*sc,:]=(im[yy*sc,:]*0.6).astype(np.uint8)
    cv2.putText(im,f'{pre}{i} y0={y0} x0={x0}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    tiles.append(im)
cv2.imwrite(out,np.vstack(tiles))
