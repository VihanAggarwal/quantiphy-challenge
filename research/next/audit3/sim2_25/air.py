import cv2,numpy as np,sys
v=sys.argv[1]
c=cv2.VideoCapture(v); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[0:300].astype(np.int16))
S=np.stack(fr); bg=np.median(S,0)
L=[]
for f in range(len(fr)):
    d=np.abs(S[f]-bg).max(2)
    m=(d>30).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    i=1+np.argmax(st[1:,4]); x,y,w,h,a=st[i]
    L.append((f,x,x+w-1,y,y+h-1,a))
L=np.array(L)
for r in L[::4]: print(r)
s=(L[:,1]>2)&(L[:,2]<1917)
p=np.polyfit(L[s,0],L[s,1],1); q=np.polyfit(L[s,0],L[s,2],1)
print('left edge px/frame %.3f  right edge %.3f'%(p[0],q[0]))
print('widths (full in frame):',(L[s,2]-L[s,1]+1).tolist())
