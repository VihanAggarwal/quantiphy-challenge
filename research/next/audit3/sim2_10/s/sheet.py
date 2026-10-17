import cv2, numpy as np, sys
c=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; scale=float(sys.argv[3]) if len(sys.argv)>3 else 0.3
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
imgs=[]
for f in frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
    im=cv2.resize(im,None,fx=scale,fy=scale)
    cv2.putText(im,str(f),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    imgs.append(im)
out=np.hstack(imgs)
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_10/png/{c}_sheet.png',out)
