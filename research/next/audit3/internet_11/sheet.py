import cv2,sys,numpy as np
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]; sc=float(sys.argv[4]) if len(sys.argv)>4 else 0.25
cap=cv2.VideoCapture(vid); imgs=[]
for f in frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
    im=cv2.resize(im,None,fx=sc,fy=sc); cv2.putText(im,str(f),(5,25),0,0.8,(0,0,255),2); imgs.append(im)
cols=int(sys.argv[5]) if len(sys.argv)>5 else 3
while len(imgs)%cols: imgs.append(np.zeros_like(imgs[0]))
rows=[np.hstack(imgs[i:i+cols]) for i in range(0,len(imgs),cols)]
cv2.imwrite(out,np.vstack(rows))
