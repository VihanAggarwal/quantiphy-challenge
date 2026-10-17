import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0045.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
ref=g[44]; win=cv2.createHanningWindow((1920,500),cv2.CV_32F)
sh=np.array([cv2.phaseCorrelate(ref[0:500],g[i][0:500],win)[0] for i in range(len(g))])
print('shift',np.round(sh,1).tolist())
for i,f in enumerate(fr):
    M=np.float32([[1,0,-sh[i,0]],[0,1,-sh[i,1]]])
    a=cv2.warpAffine(f,M,(1920,1080),borderMode=cv2.BORDER_REPLICATE)
    hsv=cv2.cvtColor(a,cv2.COLOR_BGR2HSV)
    # white: low sat, high value; restrict to desk region y>550 to avoid bowl? bowl is also white (x<560,y 540-730)
    m=((hsv[:,:,1]<45)&(hsv[:,:,2]>170)).astype(np.uint8)
    m[:560]=0
    m[540:740,120:570]=0  # bowl region (approx full-res)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[k]
        if ar<3000: continue
        print(i,'cx %.1f cy %.1f x %d-%d y %d-%d w %d h %d area %d'%(cen[k][0],cen[k][1],x,x+w,y,y+h,w,h,ar))
