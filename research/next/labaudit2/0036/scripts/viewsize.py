import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/'
Z=json.load(open('scripts/size2.json'))
tiles=[]
for v in ['captured_0036','captured_0036s']:
    row=[]
    for k in [5,22,23,33,34,35]:
        z=Z[v][str(k)]; u=int(round(z['u'])); c=int(round((z['top']+z['bot'])/2))
        im=cv2.imread(S+f'{v}/f{k:02d}.png')[c-35:c+35,u-45:u+45]
        im=cv2.resize(im,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST)
        for y in [z['top'],z['bot']]:
            yy=int(round((y-(c-35))*4)); cv2.line(im,(0,yy),(40,yy),(0,0,255),1); cv2.line(im,(320,yy),(360,yy),(0,0,255),1)
        cv2.putText(im,'%d d=%.1f'%(k,z['d']),(5,20),0,0.6,(0,0,255),2)
        row.append(im)
    tiles.append(np.hstack(row))
cv2.imwrite('img/size_marks.png',np.vstack(tiles))
