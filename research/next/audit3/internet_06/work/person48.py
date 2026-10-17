import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0048.mp4')
frames=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frames.append(f)
g0=cv2.cvtColor(frames[0],cv2.COLOR_BGR2GRAY).astype(np.float32)
win=cv2.createHanningWindow((1300,200),cv2.CV_32F)
def drift(i):
    g=cv2.cvtColor(frames[i],cv2.COLOR_BGR2GRAY).astype(np.float32)
    # region right part of wall (person is left->center) use rows 300-500 cols 600-1900? person may enter; use top rows 100-300
    (dx,dy),r=cv2.phaseCorrelate(g0[60:260,600:1900],g[60:260,600:1900],win)
    return dx,dy
bgi=25
dbg=drift(bgi)
bg=frames[bgi]
for i in range(66,109,3):
    dx,dy=drift(i)
    M=np.float32([[1,0,dx-dbg[0]],[0,1,dy-dbg[1]]])
    b=cv2.warpAffine(bg,M,(1920,1080),borderMode=cv2.BORDER_REPLICATE)
    d=cv2.absdiff(frames[i],b).max(2)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    m[930:,:]=0  # exclude reflection on floor? feet around 880-1000
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    ys,xs=np.where(lab==k)
    # head/torso x: mean x of rows y..y+250
    sel=ys<y+250
    print(i,round(i/30,2),'bbox',x,y,w,h,'top',y,'bottom',y+h,'upper-cx',round(xs[sel].mean(),1),'drift',round(dx,1),round(dy,1))
