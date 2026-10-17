import cv2, numpy as np, sys
vids=sys.argv[2:]; out=sys.argv[1]
tiles=[]
for v in vids:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.set(cv2.CAP_PROP_POS_FRAMES, n//3)
    ok,f=cap.read()
    f=cv2.resize(f,(540,540))
    cv2.putText(f,v.replace('simulation_',''),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    tiles.append(f)
while len(tiles)%4: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[i:i+4]) for i in range(0,len(tiles),4)]
cv2.imwrite(out,np.vstack(rows))
