import cv2, numpy as np, sys
R='/home/user/quantiphy-challenge/data/QuantiPhy/'
ims=[]
for v in sys.argv[1:]:
    c=cv2.VideoCapture(R+v+'.mp4'); n=int(c.get(cv2.CAP_PROP_FRAME_COUNT))
    c.set(cv2.CAP_PROP_POS_FRAMES,n//2); ok,f=c.read()
    f=cv2.resize(f,(640,360)); cv2.putText(f,v,(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2); ims.append(f)
while len(ims)%3: ims.append(np.zeros_like(ims[0]))
m=np.vstack([np.hstack(ims[i:i+3]) for i in range(0,len(ims),3)])
cv2.imwrite('xref/xref_mid.jpg',m,[cv2.IMWRITE_JPEG_QUALITY,85])
