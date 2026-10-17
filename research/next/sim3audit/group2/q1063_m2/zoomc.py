from load import frames; import numpy as np, cv2, sys
F=frames(); bg=cv2.imread('bg.png').astype(int)
i=int(sys.argv[1]); x0,y0,w,h=[int(a) for a in sys.argv[2].split(',')]; sc=int(sys.argv[3]); out=sys.argv[4]
c=F[i][y0:y0+h,x0:x0+w].astype(int); d=np.abs(c-bg[y0:y0+h,x0:x0+w]).sum(2)
d=np.clip(d*2,0,255).astype(np.uint8)
a=cv2.resize(F[i][y0:y0+h,x0:x0+w],None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
b=cv2.resize(cv2.cvtColor(d,cv2.COLOR_GRAY2BGR),None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
for img in (a,b):
    for gx in range(0,w,10): cv2.line(img,(gx*sc,0),(gx*sc,h*sc),(0,200,255) if gx%50==0 else (80,80,80),1)
    for gy in range(0,h,10): cv2.line(img,(0,gy*sc),(w*sc,gy*sc),(0,200,255) if gy%50==0 else (80,80,80),1)
cv2.putText(a,f'{i} org=({x0},{y0}) grid10',(5,20),0,0.6,(0,0,255),2)
cv2.imwrite(out,np.vstack([a,b]))
