import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/simulation_0179.mp4'); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im.astype(np.int16))
def box(f,b,th=30):
    d=np.abs(fr[f]-fr[b]).max(2)
    m=(d>th).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    i=1+np.argmax(st[1:,4]); x,y,w,h,a=st[i]; return x,x+w-1,y,y+h-1
for f,b in [(0,59),(2,59),(59,0),(57,0),(30,0),(30,59)]:
    for th in (20,30,45):
        print(f,'bg',b,'th',th,box(f,b,th))
