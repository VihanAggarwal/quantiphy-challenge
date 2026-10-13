import cv2, sys, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
def frame(v, fi=None, w=480):
    cap=cv2.VideoCapture(D+v+'.mp4'); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, n//2 if fi is None else fi); ok,f=cap.read(); cap.release()
    h=int(f.shape[0]*w/f.shape[1]); f=cv2.resize(f,(w,h))
    cv2.putText(f,v.replace('simulation_',''),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    return f
vids=sys.argv[2:]; out=sys.argv[1]
fs=[frame(v) for v in vids]
h=max(f.shape[0] for f in fs)
fs=[cv2.copyMakeBorder(f,0,h-f.shape[0],0,0,cv2.BORDER_CONSTANT) for f in fs]
rows=[np.hstack(fs[i:i+3]+[np.zeros_like(fs[0])]*(3-len(fs[i:i+3]))) for i in range(0,len(fs),3)]
cv2.imwrite(out,np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,80])
