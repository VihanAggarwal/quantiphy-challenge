import cv2, numpy as np, json
T=json.load(open('track_red.json'))
def frames(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); out=[]
    while True:
        ok,f=c.read()
        if not ok: break
        out.append(f)
    return out
for v,tag in [('captured_0010','a'),('captured_0010s','s'),('captured_0010X','x')]:
    F=frames(v)
    tiles=[]
    for j in [3,8,11,12,14,15,16,17,24,36]:
        r=T['captured_0010s'][j]; cx,cy=int(r[1]),int(r[2])
        c=F[j][cy-40:cy+40,cx-40:cx+40]
        c=cv2.resize(c,(240,240),interpolation=cv2.INTER_NEAREST)
        cv2.putText(c,str(j),(5,20),0,0.6,(0,0,0),2)
        tiles.append(c)
    cv2.imwrite(f'frames/crops_{tag}.png',np.hstack(tiles[:5]+[])) 
    cv2.imwrite(f'frames/crops2_{tag}.png',np.hstack(tiles[5:]))
