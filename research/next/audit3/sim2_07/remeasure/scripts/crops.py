import cv2, numpy as np, json, sys
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
tr=json.load(open(sys.argv[4]))
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr={}
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames: fr[i]=f
    i+=1
tiles=[]
for i in frames:
    r=tr[str(i)] if str(i) in tr else tr.get(i)
    cx,cy=int(round(r['cx'])),int(round(r['cy']))
    h=24
    crop=fr[i][max(0,cy-h):cy+h,max(0,cx-h):cx+h]
    crop=cv2.copyMakeBorder(crop,0,2*h-crop.shape[0],0,2*h-crop.shape[1],cv2.BORDER_CONSTANT)
    z=cv2.resize(crop,(384,384),interpolation=cv2.INTER_NEAREST)
    for k in range(0,384,8*5): 
        cv2.line(z,(k,0),(k,383),(0,0,255) if (k//40)%2==0 else (255,0,0),1); cv2.line(z,(0,k),(383,k),(0,0,255) if (k//40)%2==0 else (255,0,0),1)
    cv2.putText(z,f'{i} ({cx-h},{cy-h})',(4,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)
    tiles.append(z)
cv2.imwrite(out,np.hstack(tiles))
