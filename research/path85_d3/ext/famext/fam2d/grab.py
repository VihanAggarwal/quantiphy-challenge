import sys, cv2, numpy as np
sys.path.insert(0,'/home/user/quantiphy-challenge')
from qp.data import _video_index, TEST_DIR
idx=_video_index(TEST_DIR)
vids=sys.argv[2:]; out=sys.argv[1]
tiles=[]
for v in vids:
    cap=cv2.VideoCapture(str(idx[v])); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    row=[]
    for p in (0.0,0.5,0.95):
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(p*(n-1))); ok,im=cap.read()
        if not ok: im=np.zeros((360,640,3),np.uint8)
        h,w=im.shape[:2]; s=480/w; im=cv2.resize(im,(480,int(h*s)))
        im=cv2.resize(im,(480,270)) if im.shape[0]!=270 else im
        cv2.putText(im,f'{v} {p}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        row.append(im)
    tiles.append(np.hstack(row))
cv2.imwrite(out,np.vstack(tiles))
