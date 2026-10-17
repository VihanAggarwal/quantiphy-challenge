import cv2, numpy as np, pandas as pd, sys
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; outn=sys.argv[3]
e=pd.read_csv(f'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/{vid}_eagle.csv').set_index('frame')
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4'); fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
tiles=[]
for f in frames:
    cx,cy=int(e.loc[f,'cx']),int(e.loc[f,'cy'])
    c=fr[f][cy-25:cy+25,cx-35:cx+35]
    c=cv2.resize(c,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)
    cv2.putText(c,str(f),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    tiles.append(c)
rows=[np.hstack(tiles[i:i+4]) for i in range(0,len(tiles),4)]
w=max(r.shape[1] for r in rows); rows=[np.pad(r,((0,0),(0,w-r.shape[1]),(0,0))) for r in rows]
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/frames/{outn}.png',np.vstack(rows))
