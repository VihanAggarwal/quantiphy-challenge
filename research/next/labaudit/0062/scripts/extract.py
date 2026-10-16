import cv2, numpy as np, sys, os
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
O='/home/user/quantiphy-challenge/research/next/labaudit/0062/'
frames={}
for s in ['','s','x']:
    c=cv2.VideoCapture(D+'captured_0062%s.mp4'%s)
    fs=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fs.append(f)
    frames[s]=np.array(fs)
    print(s, len(fs))
# contact sheet for o: every 4th frame, scaled 0.25
for s in ['','s','x']:
    fs=frames[s]
    idx=list(range(0,49,4))
    tiles=[cv2.putText(cv2.resize(fs[i],(320,180)).copy(),str(i),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2) for i in idx]
    while len(tiles)%4: tiles.append(np.zeros_like(tiles[0]))
    rows=[np.hstack(tiles[k:k+4]) for k in range(0,len(tiles),4)]
    cv2.imwrite(O+'grid_%s.jpg'%(s or 'o'), np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,85])
