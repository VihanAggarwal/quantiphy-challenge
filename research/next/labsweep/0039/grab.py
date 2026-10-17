import cv2, sys
vid, frames, out = sys.argv[1], [int(x) for x in sys.argv[2].split(',')], sys.argv[3]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]; i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames: fr.append(f)
    i+=1
scale=float(sys.argv[4]) if len(sys.argv)>4 else 0.5
import numpy as np
fr=[cv2.resize(f,None,fx=scale,fy=scale) for f in fr]
for k,f in zip(frames,fr): cv2.putText(f,str(k),(10,30),0,1,(0,0,255),2)
rows=[np.hstack(fr[i:i+2]) if len(fr[i:i+2])==2 else np.hstack([fr[i],np.zeros_like(fr[i])]) for i in range(0,len(fr),2)]
cv2.imwrite(out,np.vstack(rows))
