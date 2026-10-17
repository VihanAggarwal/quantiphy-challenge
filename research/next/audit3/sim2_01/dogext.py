import cv2, numpy as np, sys
c=sys.argv[1]; y0,y1=int(sys.argv[2]),int(sys.argv[3])
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
i=0
W=[]
while True:
    ok,f=cap.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    s=hsv[...,1]; v=hsv[...,2]
    m=((s>70)&(v>60)).astype(np.uint8); m[:y0]=0; m[y1:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4]); x,y,w,h,a=st[j]
    # include nearby comps (tail pieces) within 40px
    xs=[x,x+w]; ys=[y,y+h]
    for k in range(1,n):
        if k==j or st[k,4]<30: continue
        X,Y,Wd,H,A=st[k]
        if X<x+w+40 and X+Wd>x-40 and Y<y+h+40 and Y+H>y-40:
            xs+= [X,X+Wd]; ys+=[Y,Y+H]
    W.append((i,min(xs),max(xs),min(ys),max(ys),a))
    i+=1
for r in W[::3]: print('f%d x %d-%d (%d) y %d-%d (%d) area %d'%(r[0],r[1],r[2],r[2]-r[1],r[3],r[4],r[4]-r[3],r[5]))
