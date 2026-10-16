import cv2, numpy as np, json
v='captured_0036'
T=json.load(open('scripts/trk_o.json'))
ims=[]
for k in [5,13,17,21,22,23,27,31,33,34,35,36]:
    im=cv2.imread(f'frames/{v}/f{k:02d}.png')
    cx,cy=int(T[str(k)]['cx']),int(T[str(k)]['cy'])
    c=im[cy-40:cy+40,cx-50:cx+50]
    c=cv2.resize(c,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST)
    cv2.putText(c,str(k),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    ims.append(c)
rows=[np.hstack(ims[i:i+4]) for i in range(0,12,4)]
cv2.imwrite('frames/crops_ball.png',np.vstack(rows))
