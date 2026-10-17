import cv2, numpy as np, sys
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/'
cents={21:(553,454),22:(569,457),23:(586,461),34:(838,513),35:(870,520),36:(935,530)}
tiles=[]
for v in ['captured_0036','captured_0036x']:
    row=[]
    for k,(x,y) in cents.items():
        im=cv2.imread(S+f'{v}/f{k:02d}.png')[y-40:y+40,x-50:x+50]
        im=cv2.resize(im,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
        cv2.putText(im,str(k),(5,25),0,0.8,(0,0,255),2)
        row.append(im)
    tiles.append(np.hstack(row))
cv2.imwrite('img/crops.png',np.vstack(tiles))
