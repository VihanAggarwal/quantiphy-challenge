import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0030/frames'
T2=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track2.json'))
T3=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit/0030/track3.json'))
idx=[4,5,6,9,10,11,14,15,16,19,20,21]
ims=[]
for i in idx:
    im=cv2.imread(f'{d}/s_{i:02d}.png')
    a=T2['s'][i]; b=T3['s'][i]
    x,y=int(round(a['cx'])),int(round(a['cy']))
    big=cv2.resize(im[y-45:y+45,x-60:x+60],None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
    def P(px,py): return (int((px-(x-60))*3),int((py-(y-45))*3))
    cv2.drawMarker(big,P(a['cx'],a['cy']),(0,255,0),cv2.MARKER_CROSS,14,2)
    cv2.drawMarker(big,P(b['cx'],b['cy']),(255,0,0),cv2.MARKER_TILTED_CROSS,14,2)
    cv2.line(big,P(b['cx']-30,b['top']),P(b['cx']+30,b['top']),(255,0,255),1)
    cv2.line(big,P(b['cx']-30,b['bot']),P(b['cx']+30,b['bot']),(255,0,255),1)
    cv2.putText(big,f's{i}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)
    ims.append(big)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/labaudit/0030/overlay_centres.png',np.vstack([np.hstack(ims[k:k+3]) for k in range(0,12,3)]))
