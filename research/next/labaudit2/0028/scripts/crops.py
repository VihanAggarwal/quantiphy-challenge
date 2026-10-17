import cv2, numpy as np, sys
# zoomed crops of the ball region for several frames of one render, tiled
V=sys.argv[1]; frames=[int(a) for a in sys.argv[2].split(',')]; x0,y0,w,h=[int(a) for a in sys.argv[3].split(',')]; z=int(sys.argv[4]); out=sys.argv[5]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{V}.mp4'); F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f)
tiles=[]
for i in frames:
    c=cv2.resize(F[i][y0:y0+h,x0:x0+w],(w*z,h*z),interpolation=cv2.INTER_NEAREST)
    cv2.putText(c,str(i),(5,25),0,0.9,(0,0,255),2); tiles.append(c)
n=len(tiles); cols=min(n,6); rows=(n+cols-1)//cols
blank=np.zeros_like(tiles[0]); tiles+= [blank]*(rows*cols-n)
img=np.vstack([np.hstack(tiles[r*cols:(r+1)*cols]) for r in range(rows)])
cv2.imwrite(out,img)
