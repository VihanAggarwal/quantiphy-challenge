import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
for name in ['captured_0023s_48','captured_0023_48','captured_0023_00']:
    f=cv2.imread(D+f'frames/{name}.png').astype(np.float32)
    gray=cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
    g=cv2.GaussianBlur(gray,(5,5),1.2)
    gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
    P=[];Q=[]
    for x in range(300,900,4):
        col=-gy[518:545,x]; i=np.argmax(col)
        # subpixel parabola
        if 0<i<len(col)-1:
            a,b,c=col[i-1],col[i],col[i+1]; d=0.5*(a-c)/(a-2*b+c)
        else: d=0
        P.append((x,518+i+d))
        col2=gy[545:575,x]; j=np.argmax(col2); Q.append((x,545+j))  # bottom of front face (dark->bg?) 
    P=np.array(P); 
    p2=np.polyfit(P[:,0]-640,P[:,1],2); p1=np.polyfit(P[:,0]-640,P[:,1],1)
    r2=P[:,1]-np.polyval(p2,P[:,0]-640); r1=P[:,1]-np.polyval(p1,P[:,0]-640)
    print(name,'front edge quad',np.round(p2,6),'sd1 %.2f sd2 %.2f'%(r1.std(),r2.std()))
    print('  sag at ends rel. to chord (px): %.2f'%(p2[0]*(320**2)))
