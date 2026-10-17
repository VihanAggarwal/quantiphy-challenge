import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0020.mp4')
fr=[]
for i in range(131):
    ok,f=c.read()
    if not ok: break
    if i in (0,40,128): fr.append(f)
# background: median of 3 frames (person moves little, though)
bg=np.median(np.stack(fr),0).astype(np.uint8)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/sim3audit/group3/frames/simulation_0020/bg.png',bg)
g=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY)
roi=g[762:842,:].copy()
e=cv2.Canny(cv2.GaussianBlur(roi,(3,3),0),20,60)
lines=cv2.HoughLinesP(e,1,np.pi/360,25,minLineLength=25,maxLineGap=4)
segs=[]
for l in lines.reshape(-1,4):
    x1,y1,x2,y2=l; y1+=762;y2+=762
    if abs(y2-y1)<8: continue
    segs.append((x1,y1,x2,y2))
segs.sort()
for s in segs:
    x1,y1,x2,y2=s
    print(s, 'dx/dy=%.3f'%((x2-x1)/(y2-y1)))
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/group3/s20_segs.npy',np.array(segs))
