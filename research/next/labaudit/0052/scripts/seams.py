import cv2, numpy as np
f = cv2.imread('frames/o_00.png').astype(float)
# median over all frames to remove person
fr=[cv2.imread(f'frames/o_{n:02d}.png').astype(float) for n in range(0,49,3)]
med=np.median(np.stack(fr),0)
cv2.imwrite('median_o.png',med.astype(np.uint8))
g=cv2.GaussianBlur(med.mean(2),(1,5),0)
guess={'L1':38,'L2':200,'L3':318,'L4':405,'B1':608,'B2':710,'B3':828,'R1':962,'R2':1098}
res={}
for k,x0 in guess.items():
    pts=[]
    for y in range(140,500,10):
        # use initial guess track
        xs=np.arange(x0-10,x0+11)
        prof=g[y,xs]
        # seams: find min
        i=np.argmin(prof)
        # check contrast
        c=np.median(prof)-prof[i]
        if c>6: pts.append((y,xs[i]))
    pts=np.array(pts)
    if len(pts)<5: print(k,'few',len(pts)); continue
    A=np.c_[np.ones(len(pts)),pts[:,0]]
    sol,*_=np.linalg.lstsq(A,pts[:,1],rcond=None)
    r=pts[:,1]-A@sol
    keep=np.abs(r)<2
    sol,*_=np.linalg.lstsq(A[keep],pts[keep,1],rcond=None)
    res[k]=sol
    print(k,len(pts),keep.sum(),'x=%.1f + %.4f*y'%tuple(sol), 'yrange',pts[keep,0].min(),pts[keep,0].max())
np.save('seams.npy',res)
