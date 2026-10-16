import cv2, numpy as np
R='/home/user/quantiphy-challenge/data/QuantiPhy/'
def frame(v,i):
    c=cv2.VideoCapture(R+v+'.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=c.read(); return f
a=frame('captured_0015',0); 
for v in ['captured_0041','captured_0047']:
    b=frame(v,0)
    ga=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype(np.float32); gb=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY).astype(np.float32)
    # mask person region in 0015 left; use right half (x>600) for phase correlation
    sa=ga[:,600:1250]; sb=gb[:,600:1250]
    sh,resp=cv2.phaseCorrelate(sa,sb)
    print(v,'shift',sh,'resp',resp)
    blend=cv2.addWeighted(a,0.5,b,0.5,0)
    cv2.imwrite(f'xref/blend_{v[-4:]}.jpg',blend,[cv2.IMWRITE_JPEG_QUALITY,85])
