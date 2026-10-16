import cv2, numpy as np, sys
tag = sys.argv[1]; idx = [int(x) for x in sys.argv[2].split(',')]
x0,y0,x1,y1 = [int(v) for v in sys.argv[3].split(',')]
scale = float(sys.argv[4]) if len(sys.argv)>4 else 1.0
tiles=[]
for i in idx:
    f = cv2.imread('f_%s_%02d.png'%(tag,i))[y0:y1,x0:x1]
    f = cv2.resize(f,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    cv2.putText(f,str(i),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    tiles.append(f)
cols=4
rows=[np.hstack(tiles[r*cols:(r+1)*cols] + [np.zeros_like(tiles[0])]*(cols-len(tiles[r*cols:(r+1)*cols]))) for r in range((len(tiles)+cols-1)//cols)]
cv2.imwrite(sys.argv[5], np.vstack(rows))
