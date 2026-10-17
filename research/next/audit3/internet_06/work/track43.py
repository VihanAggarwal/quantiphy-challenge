import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0043.mp4')
frames=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frames.append(f)
bg=np.median(np.stack([cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in frames[::6]]),axis=0).astype(np.uint8)
for i,f in enumerate(frames):
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    # white: low sat high val, in table region y 750-1000
    m=((hsv[:,:,1]<60)&(hsv[:,:,2]>170)).astype(np.uint8)
    m[:760,:]=0; m[960:,:]=0
    d=(cv2.absdiff(g,bg)>25).astype(np.uint8)
    mm=m&d
    n,lab,st,cen=cv2.connectedComponentsWithStats(mm)
    if n>1:
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        if a>500: print(i, round(i/30,3), 'x',x,'y',y,'w',w,'h',h,'a',a,'cx',round(cen[k][0],1),'cy',round(cen[k][1],1))
