import cv2, numpy as np, sys
r=sys.argv[1]; frames=list(map(int,sys.argv[2].split(','))); x0,y0,x1,y1=map(int,sys.argv[3:7]); s=float(sys.argv[7]); out=sys.argv[8]
tiles=[]
for f in frames:
    im=cv2.imread(f'frames/{r}_{f:02d}.png')[y0:y1,x0:x1]
    im=cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
    cv2.putText(im,f'f{f} t={f/24:.2f}',(4,16),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
    tiles.append(im)
n=len(tiles); cols=int(sys.argv[9]) if len(sys.argv)>9 else 4
rows=[]
for i in range(0,n,cols):
    row=tiles[i:i+cols]
    while len(row)<cols: row.append(np.zeros_like(tiles[0]))
    rows.append(np.hstack(row))
cv2.imwrite(out,np.vstack(rows))
