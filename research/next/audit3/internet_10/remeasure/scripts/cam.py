import cv2, numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
frames=[]
ref=None
res=[]
i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    # regions: building (static) x 0-1800, y 0-700 ; court bottom
    rois={'bld':(slice(100,700),slice(100,1800)),'court':(slice(1300,2100),slice(200,3600)),'hedgeR':(slice(800,1050),slice(2900,3700))}
    if ref is None: ref={k:g[v] for k,v in rois.items()}; win={k:cv2.createHanningWindow(ref[k].shape[::-1],cv2.CV_32F) for k in rois}
    row=[i]
    for k,v in rois.items():
        (dx,dy),r=cv2.phaseCorrelate(ref[k],g[v],win[k])
        row+= [dx,dy]
    res.append(row); i+=1
res=np.array(res)
np.savetxt('research/next/audit3/internet_10/remeasure/cam_shift.txt',res,fmt='%.2f',header='frame bld_dx bld_dy court_dx court_dy hedgeR_dx hedgeR_dy')
for r in res[::6]: print(' '.join('%.1f'%x for x in r))
print(res[-1])
