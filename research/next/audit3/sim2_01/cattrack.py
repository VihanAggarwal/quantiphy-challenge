import cv2, numpy as np, sys
clips=sys.argv[1:]
for c in clips:
    cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
    rows=[]
    i=0
    while True:
        ok,f=cap.read()
        if not ok: break
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        m=(g<40).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n>1:
            k=1+np.argmax(st[1:,4])
            x,y,w,h,a=st[k]
            ys,xs=np.nonzero(lab==k)
            rows.append((i,x,x+w,y,y+h,a,cen[k][0],cen[k][1]))
        i+=1
    rows=np.array(rows)
    print(c)
    for r in rows[::4]: print('  f%2d x %4d-%4d y %4d-%4d area %6d cx %.1f cy %.1f'%tuple(r))
    f=rows[:,0]
    for col,name in ((1,'left'),(2,'right'),(6,'cx')):
        p=np.polyfit(f,rows[:,col],1); print('  slope',name,'%.3f'%p[0])
