import cv2,numpy as np
# independent centroid: "darkness" vs board white (255 - min channel) inside a 44x56 window, background-free (no bg subtraction)
src='captured_0014'
tr={12:(545.8,329.2),13:(546.6,340.8),14:(547.6,354.0),15:(548.3,370.0),16:(549.5,389.2)}
out=[]
for i,(x0,y0) in tr.items():
    f=cv2.imread('frames/%s_%02d.png'%(src,i)).astype(np.float32)
    x0i,y0i=int(round(x0)),int(round(y0))
    W=f[y0i-26:y0i+27,x0i-20:x0i+21]
    dark=255-W.min(2); dark=np.clip(dark-25,0,None)  # board ~ >=230
    yy,xx=np.mgrid[0:W.shape[0],0:W.shape[1]]
    cxw=(xx*dark).sum()/dark.sum()+x0i-20; cyw=(yy*dark).sum()/dark.sum()+y0i-26
    # vertical profile edges at half max
    prof=dark[:,10:31].mean(1); hm=prof.max()/2; idx=np.nonzero(prof>hm)[0]
    print(i,'dark-centroid %.1f %.1f'%(cxw,cyw),'half-max extent y %d..%d mid %.1f'%(idx[0]+y0i-26,idx[-1]+y0i-26,(idx[0]+idx[-1])/2+y0i-26))
    c=cv2.resize(f[y0i-40:y0i+40,x0i-30:x0i+30].astype(np.uint8),None,fx=4,fy=4,interpolation=cv2.INTER_CUBIC)
    cv2.circle(c,(int((cxw-x0i+30)*4),int((cyw-y0i+40)*4)),4,(0,0,255),-1)
    cv2.circle(c,(int((cxw-x0i+30)*4),int((cyw-y0i+40)*4)),int(14.5*4),(0,0,255),1)
    out.append(c)
cv2.imwrite('overlay_12_16.png',np.hstack(out))
