import cv2,numpy as np,json,sys
sfx=sys.argv[1]; frames=[int(a) for a in sys.argv[2].split(',')]; out=sys.argv[3]
tr=json.load(open('tracks.json'))[sfx if sfx else 'a']
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0037%s.mp4'%sfx)
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
tiles=[]
for i in frames:
    r=tr[i]; cx,cy=int(round(r['cx'])),int(round(r['cy']))
    t=fr[i][cy-40:cy+40,cx-40:cx+40].copy()
    t=cv2.resize(t,(240,240),interpolation=cv2.INTER_CUBIC)
    cv2.circle(t,(int((r['cx']-cx+40)*3),int((r['cy']-cy+40)*3)),3,(0,0,255),-1)
    cv2.putText(t,str(i),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    tiles.append(t)
rows=[np.hstack(tiles[k:k+5]+[np.zeros_like(tiles[0])]*(5-len(tiles[k:k+5]))) for k in range(0,len(tiles),5)]
cv2.imwrite(out,np.vstack(rows))
