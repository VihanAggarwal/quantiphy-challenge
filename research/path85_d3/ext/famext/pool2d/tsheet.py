import sys, cv2, numpy as np, os
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
out=sys.argv[1]; times=[float(x) for x in sys.argv[2].split(',')]; vids=sys.argv[3:]
rows=[]
for v in vids:
    cap=cv2.VideoCapture(D+v+'.mp4'); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    ims=[]
    for tt in times:
        fi=min(n-1,int(round(tt*fps))); cap.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,im=cap.read()
        if not ok: im=np.zeros((216,384,3),np.uint8)
        im=cv2.resize(im,(384,216)); cv2.putText(im,f'{v[-8:]} t={tt}',(5,18),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2); ims.append(im)
    rows.append(np.hstack(ims))
cv2.imwrite(out,np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,70])
