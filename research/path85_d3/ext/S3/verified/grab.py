import cv2, sys, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
O='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/merge/S3/verified/frames/'
# montage: for each video, one mid frame, scaled to width 640, tiled 2 per row
vids=sys.argv[2:]; name=sys.argv[1]
ims=[]
for v in vids:
    cap=cv2.VideoCapture(D+v+'.mp4'); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, n//3); ok,f=cap.read()
    if not ok: f=np.zeros((360,640,3),np.uint8)
    h,w=f.shape[:2]; f=cv2.resize(f,(640,int(h*640/w)))
    f=cv2.resize(f,(640,360))
    cv2.putText(f,v,(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    ims.append(f)
while len(ims)%2: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[i:i+2]) for i in range(0,len(ims),2)]
cv2.imwrite(O+name+'.jpg', np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])
