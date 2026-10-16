import cv2, numpy as np, sys, json
s=sys.argv[1]; frames=[int(a) for a in sys.argv[2].split(',')]; half=int(sys.argv[3]) if len(sys.argv)>3 else 60
scale=int(sys.argv[4]) if len(sys.argv)>4 else 3
tr=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0033/track_x_raw.json'))
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0033%s.mp4'%('' if s=='o' else s)); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
tiles=[]
for i in frames:
    cx,cy=int(tr[i][0]['cx']),int(tr[i][0]['cy'])
    x0=max(0,min(1280-2*half,cx-half)); y0=max(0,min(720-2*half,cy-half))
    t=fr[i][y0:y0+2*half,x0:x0+2*half]
    t=cv2.resize(t,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
    cv2.putText(t,'%d (%d,%d)'%(i,x0,y0),(4,18),0,0.6,(0,0,255),2)
    tiles.append(t)
out='/home/user/quantiphy-challenge/research/next/labaudit/0033/frames/crops_%s_%s.png'%(s,sys.argv[2].replace(',','-'))
cv2.imwrite(out,np.hstack(tiles)); print(out)
