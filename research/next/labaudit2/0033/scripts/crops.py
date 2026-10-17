# usage: crops.py render frames(comma) cx cy half scale out
import cv2, numpy as np, sys
R=sys.argv[1]; F=[int(a) for a in sys.argv[2].split(',')]
half=int(sys.argv[5]); sc=int(sys.argv[6]); out=sys.argv[7]
cxs=[float(a) for a in sys.argv[3].split(',')]; cys=[float(a) for a in sys.argv[4].split(',')]
if len(cxs)==1: cxs=cxs*len(F); cys=cys*len(F)
p='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0033%s.mp4'%('' if R=='o' else R)
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
tiles=[]
for i,cx,cy in zip(F,cxs,cys):
    x0=int(cx)-half; y0=int(cy)-half
    im=np.zeros((2*half,2*half,3),np.uint8)
    src=fr[i][max(y0,0):y0+2*half, max(x0,0):x0+2*half]
    im[max(0,-y0):max(0,-y0)+src.shape[0], max(0,-x0):max(0,-x0)+src.shape[1]]=src
    im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    # grid every 10 px
    for g in range(0,2*half,10):
        cv2.line(im,(g*sc,0),(g*sc,3),(0,255,0),1); cv2.line(im,(0,g*sc),(3,g*sc),(0,255,0),1)
    cv2.putText(im,'%d (%d,%d)'%(i,x0,y0),(4,16),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
    tiles.append(im)
n=len(tiles); cols=min(n,4); rows=(n+cols-1)//cols
H,W=tiles[0].shape[:2]
sheet=np.zeros((rows*H,cols*W,3),np.uint8)
for k,t in enumerate(tiles): sheet[(k//cols)*H:(k//cols+1)*H,(k%cols)*W:(k%cols+1)*W]=t
cv2.imwrite(out,sheet)
