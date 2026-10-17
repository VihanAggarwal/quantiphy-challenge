import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0052.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
ref=g[0]
# background shift using top region rows 0-600 (trees, sky) 
win=cv2.createHanningWindow((1920,600),cv2.CV_32F)
sh=np.array([cv2.phaseCorrelate(ref[0:600],g[i][0:600],win)[0] for i in range(len(g))])
print('shift every 6',np.round(sh[::6],1).tolist())
win2=cv2.createHanningWindow((1920,120),cv2.CV_32F)
sh2=np.array([cv2.phaseCorrelate(ref[960:1080],g[i][960:1080],win2)[0] for i in range(len(g))])
print('shift ground every 6',np.round(sh2[::6],1).tolist())
al=[cv2.warpAffine(f.astype(np.float32),np.float32([[1,0,-sh[i,0]],[0,1,-sh[i,1]]]),(1920,1080),borderMode=cv2.BORDER_REPLICATE) for i,f in enumerate(fr)]
bg=np.median(np.stack(al),axis=0)
for i in range(0,len(al),3):
    d=np.abs(al[i]-bg).max(axis=2)
    m=(d>40).astype(np.uint8); m[:600]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((25,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[k]
    print(i,'x %d-%d y %d-%d w %d h %d cx %.1f'%(x,x+w,y,y+h,w,h,cen[k][0]))
