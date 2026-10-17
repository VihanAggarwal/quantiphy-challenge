import cv2, sys, numpy as np
p=sys.argv[1]; reff=int(sys.argv[2]); frames=[int(v) for v in sys.argv[3].split(',')]
cap=cv2.VideoCapture(p); G={}
f=0
while True:
    ok,im=cap.read()
    if not ok: break
    if f in frames or f==reff:
        g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
        g=g-cv2.GaussianBlur(g,(0,0),8)
        G[f]=g
    f+=1
R=G[reff]; win=cv2.createHanningWindow((160,160),cv2.CV_32F)
for f in frames:
    print('frame',f)
    for y in range(40,1000,160):
        line=[]
        for x in range(0,1920-159,160):
            a=R[y:y+160,x:x+160]; b=G[f][y:y+160,x:x+160]
            (dx,dy),r=cv2.phaseCorrelate(a,b,win)
            line.append('%5.1f,%5.1f/%.2f'%(dx,dy,r) if r>0.25 else '     ----     ')
        print('y%4d '%y+' '.join(line))
