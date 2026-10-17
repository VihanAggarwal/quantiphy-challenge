import cv2, numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/simulation_0216_segmented.mp4')
fr={}
i=0
while True:
    ok,f=cap.read()
    if not ok: break
    if i in (0,48): fr[i]=f
    i+=1
for k,f in fr.items():
    m=(f.min(2)<235).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    print('frame',k)
    for j in range(1,n):
        x,y,w,h,a=st[j]
        if a>500: print('  comp x %d-%d y %d-%d w %d h %d area %d'%(x,x+w-1,y,y+h-1,w,h,a))
