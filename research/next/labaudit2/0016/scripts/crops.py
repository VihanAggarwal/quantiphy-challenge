import cv2, numpy as np
FR='/home/user/quantiphy-challenge/research/next/labaudit/0016/frames/f%s_%02d.png'
OUT='/home/user/quantiphy-challenge/research/next/labaudit2/0016/img/'
C={32:(587,256),33:(641,199),34:(689,156),35:(735,121),36:(812,77),37:(845,70),38:(872,71),39:(894,77),40:(913,91),41:(930,110)}
for rend in 'ox':
    tiles=[]
    for i,(cx,cy) in C.items():
        im=cv2.imread(FR%(rend,i))
        pad=cv2.copyMakeBorder(im,120,120,120,120,cv2.BORDER_CONSTANT)
        t=pad[cy:cy+240,cx:cx+240].copy()
        cv2.putText(t,str(i),(5,20),0,0.7,(0,0,255),2)
        cv2.drawMarker(t,(120,120),(0,0,255),cv2.MARKER_CROSS,10,1)
        tiles.append(t)
    row1=np.hstack(tiles[:5]); row2=np.hstack(tiles[5:])
    cv2.imwrite(OUT+'ballcrops_%s.png'%rend,np.vstack([row1,row2]))
