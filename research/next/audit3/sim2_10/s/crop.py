import cv2, sys
c=sys.argv[1]; f=int(sys.argv[2]); x0,y0,x1,y1=[int(v) for v in sys.argv[3].split(',')]; z=float(sys.argv[4]); out=sys.argv[5]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
cr=im[y0:y1,x0:x1].copy()
# grid lines every 50px
for x in range(((x0+49)//50)*50,x1,50): cr[:,x-x0]=(0,0,255) if x%100==0 else (0,255,255)
for y in range(((y0+49)//50)*50,y1,50): cr[y-y0,:]=(0,0,255) if y%100==0 else (0,255,255)
cr=cv2.resize(cr,None,fx=z,fy=z,interpolation=cv2.INTER_NEAREST)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/sim2_10/png/'+out,cr)
