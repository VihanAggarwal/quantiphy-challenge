import cv2,sys,numpy as np
v=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
ims=[]
for fi in frames:
    cap.set(1,fi); ok,f=cap.read()
    f=cv2.resize(f,(640,360)); cv2.putText(f,str(fi),(10,30),0,1,(0,0,255),2); ims.append(f)
while len(ims)%2: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[i:i+2]) for i in range(0,len(ims),2)]
cv2.imwrite(out,np.vstack(rows))
