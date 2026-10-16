import cv2, numpy as np
from edgefit import edge_line, inter
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0029.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
img=np.median(np.stack(fr[36:49]),axis=0).astype(np.uint8)
cv2.imwrite('c29_med_late.png',img)
g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
# use a 'brownness' channel for table vs gray/white: R-B
rb=(img[...,2].astype(np.float32)-img[...,0].astype(np.float32))
rb=3*cv2.GaussianBlur(rb,(3,3),0)
FL=(208,540); FR=(1140,592); BR=(912,463); BL=(445,452)
front,pf,rf=edge_line(g,FL,FR,trim=(0.05,0.95),half=8)      # top surface (light) vs front face (dark)
left,pl,rl=edge_line(rb,FL,BL,trim=(0.1,0.9),half=8)
right,pr,rr=edge_line(rb,FR,BR,trim=(0.1,0.9),half=8)
back,pb,rbk=edge_line(g,BL,BR,trim=(0.08,0.92),half=6)
for nm,pp,r in [('front',pf,rf),('left',pl,rl),('right',pr,rr),('back',pb,rbk)]:
    print(nm,len(pp),'rms',round(float(np.sqrt(np.mean(r**2))),2))
C=np.array([inter(left,front),inter(front,right),inter(right,back),inter(back,left)])
print('corners FL,FR,BR,BL',np.round(C,1).tolist())
np.save('c29_table_corners.npy',C)
np.save('c29_back_line.npy',back)
