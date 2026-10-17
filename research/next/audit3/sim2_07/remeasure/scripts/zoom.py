import cv2, numpy as np, json, sys
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; ell=json.load(open(sys.argv[3])); out=sys.argv[4]
E={int(r[0]):r for r in ell}
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr={};i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames: fr[i]=f
    i+=1
tiles=[]
Z=12;h=20
for i in frames:
    cx,cy=int(round(E[i][1])),int(round(E[i][2]))
    crop=fr[i][cy-h:cy+h,cx-h:cx+h].astype(np.float32)
    Y=crop@np.array([0.114,0.587,0.299])
    lo,hi=np.percentile(Y,1),np.percentile(Y,99)
    Yn=np.clip((Y-lo)/(hi-lo)*255,0,255).astype(np.uint8)
    for img in (cv2.cvtColor(Yn,cv2.COLOR_GRAY2BGR), crop.astype(np.uint8)):
        z=cv2.resize(img,(2*h*Z,2*h*Z),interpolation=cv2.INTER_NEAREST)
        # circle of diameter 23 and 25 centred at ellipse centre
        ccx=(E[i][1]-(cx-h)+0.5)*Z; ccy=(E[i][2]-(cy-h)+0.5)*Z
        cv2.circle(z,(int(ccx),int(ccy)),int(11.5*Z),(255,0,0),1)
        cv2.circle(z,(int(ccx),int(ccy)),int(12.5*Z),(0,0,255),1)
        cv2.putText(z,str(i),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2)
        tiles.append(z)
cv2.imwrite(out,np.hstack(tiles))
