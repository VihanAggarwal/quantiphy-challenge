import cv2, sys, glob, os, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/'
idx={os.path.splitext(os.path.basename(p))[0].strip():p for p in glob.glob(V+'**/*.mp4',recursive=True)}
vid=sys.argv[1]; ts=[float(x) for x in sys.argv[2].split(',')]; scale=float(sys.argv[3]) if len(sys.argv)>3 else 0.4
cap=cv2.VideoCapture(idx[vid]); fps=cap.get(cv2.CAP_PROP_FPS); n=cap.get(cv2.CAP_PROP_FRAME_COUNT)
print(vid,'fps',fps,'frames',n,'dur',n/fps,'size',cap.get(3),cap.get(4))
ims=[]
for t in ts:
    cap.set(cv2.CAP_PROP_POS_FRAMES,int(round(t*fps))); ok,im=cap.read()
    if not ok: continue
    im=cv2.resize(im,None,fx=scale,fy=scale); cv2.putText(im,'t=%.2f'%t,(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2); ims.append(im)
rows=[np.hstack(ims[i:i+3]) if len(ims[i:i+3])==3 else np.hstack(ims[i:i+3]+[np.zeros_like(ims[0])]*(3-len(ims[i:i+3]))) for i in range(0,len(ims),3)]
out=np.vstack(rows); p='frames/%s.jpg'%vid; cv2.imwrite(p,out,[cv2.IMWRITE_JPEG_QUALITY,75]); print(p,out.shape)
