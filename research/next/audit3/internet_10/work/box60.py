import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0060.mp4')
k=0
while True:
    ok,f=c.read()
    if not ok: break
    if 40<=k<=95 or k in (0,10,20,30):
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float)
        # drift: left edge of dark band at rows 150 (top, away from box path?) and 950
        bx=[]
        for y in (150,950):
            row=g[y-3:y+4,1100:1700].mean(0); d=np.where(row<60)[0]; bx.append(1100+d.min())
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        b,gg,r=[f[:,:,i].astype(int) for i in range(3)]
        m=((r-gg)>35)&((r-b)>15)&(hsv[:,:,1]>60)
        m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        s=''
        if n>1:
            order=np.argsort(-st[1:,4])[:2]+1
            for j in order:
                x,y,w,h,a=st[j]
                if a>300: s+=' [x%d-%d y%d-%d a%d]'%(x,x+w,y,y+h,a)
        print(k,'band',bx,s)
    k+=1
