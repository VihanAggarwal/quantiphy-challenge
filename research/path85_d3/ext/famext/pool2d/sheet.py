import sys, cv2, numpy as np, os
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
out=sys.argv[1]; vids=sys.argv[2:]
rows=[]
for v in vids:
    p=D+v+'.mp4'
    if not os.path.exists(p): print('missing',p); continue
    cap=cv2.VideoCapture(p); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    ims=[]
    for f in (0.0,0.5,0.95):
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(f*(n-1))); ok,im=cap.read()
        if not ok: im=np.zeros((270,480,3),np.uint8)
        im=cv2.resize(im,(480,270)); cv2.putText(im,f'{v} {f} n={n} fps={fps:.0f}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,0,255),2); ims.append(im)
    rows.append(np.hstack(ims))
cv2.imwrite(out,np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,70])
