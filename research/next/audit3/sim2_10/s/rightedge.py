import cv2, numpy as np, sys
c=sys.argv[1]; thr=int(sys.argv[2]); y0,y1=[int(v) for v in sys.argv[3].split(',')]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
R=[];f=0
while True:
    ok,im=cap.read()
    if not ok: break
    m=(im.astype(int).min(axis=2)<thr)[y0:y1]
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    # largest component
    i=1+np.argmax(st[1:,4]); x,y,w,h,a=st[i]
    R.append((f,x+w,x,y+y0,h)); f+=1
R=np.array(R,float)
p=np.polyfit(R[:,0],R[:,1],1); print(c,'right edge slope',p[0].round(3), 'f0..74 right',R[0,1],R[-1,1])
print('right x every 6:',R[::6,1].astype(int))
