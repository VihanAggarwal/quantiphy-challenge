import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0229.mp4')
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f.astype(np.float32))
bg=np.median(np.stack(fr[36:]),axis=0)
g=bg.mean(axis=2)
hsv=cv2.cvtColor(bg.astype(np.uint8),cv2.COLOR_BGR2HSV).astype(np.float32)
# horizontal profile across the board frame at several rows: red channel - green (frame is orange-ish)
for y in (450,550,650):
    r=bg[y,:,2]-bg[y,:,1]
    print('row',y,'R-G left region', [(x,int(r[x])) for x in range(300,345,3)])
    print('row',y,'R-G right region', [(x,int(r[x])) for x in range(1670,1705,3)])
for x in (700,1200):
    r=bg[:,x,2]-bg[:,x,1]
    print('col',x,'R-G top', [(y,int(r[y])) for y in range(285,310,2)])
    print('col',x,'R-G bottom', [(y,int(r[y])) for y in range(720,760,2)])
    print('col',x,'gray 150-190', [(y,int(g[y,x])) for y in range(150,195,3)])
    print('col',x,'gray 935-970', [(y,int(g[y,x])) for y in range(930,975,3)])
