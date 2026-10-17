from load import frames; import numpy as np, cv2, json, sys
F=frames(); T=json.load(open('track.json'))
ids=[int(a) for a in sys.argv[2].split(',')]; name=sys.argv[1]; sc=float(sys.argv[3]) if len(sys.argv)>3 else 4
tiles=[]
for i in ids:
    t=T[i]; cx=int((t['x0']+t['x1'])/2); cy=int((t['y0']+t['y1'])/2)
    hw,hh=95,60
    c=F[i][cy-hh:cy+hh, cx-hw:cx+hw].copy()
    c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
    # grid every 10 px
    for gx in range(0,2*hw,10):
        cv2.line(c,(int(gx*sc),0),(int(gx*sc),6),(0,255,255),1)
    for gy in range(0,2*hh,10):
        cv2.line(c,(0,int(gy*sc)),(6,int(gy*sc)),(0,255,255),1)
    cv2.putText(c,f'{i} org=({cx-hw},{cy-hh})',(10,25),0,0.7,(0,0,255),2)
    tiles.append(c)
cols=2
while len(tiles)%cols: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[k:k+cols]) for k in range(0,len(tiles),cols)]
cv2.imwrite(name,np.vstack(rows))
