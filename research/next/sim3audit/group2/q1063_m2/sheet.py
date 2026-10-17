from load import frames; import numpy as np, cv2, json, sys
F=frames(); B=json.load(open('birdbox.json'))
start=int(sys.argv[1]); n=12
tiles=[]
for i in range(start,min(start+n,60)):
    b=B[i]; cx=int((b['x0']+b['x1'])/2); cy=int((b['y0']+b['y1'])/2)
    c=F[i][cy-75:cy+75, cx-110:cx+110].copy()
    c=cv2.resize(c,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
    cv2.putText(c,f'{i} ({cx-110},{cy-75})',(5,22),0,0.6,(0,0,255),2)
    tiles.append(c)
while len(tiles)%4: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[k:k+4]) for k in range(0,len(tiles),4)]
cv2.imwrite(f'sheet{start:02d}.png',np.vstack(rows))
