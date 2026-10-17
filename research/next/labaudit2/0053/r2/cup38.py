import cv2,numpy as np,sys
v=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
acc=[]
while True:
    ok,f=c.read()
    if not ok: break
    acc.append(f[y0:y1,x0:x1].astype(float))
a=np.median(np.array(acc),0)
lum=a.max(2)
# alpha from brightness vs black bg (cup white ~ 200+)
for y in range(0,y1-y0,2):
    row=lum[y]
    xs=np.where(row>60)[0]
    if len(xs):
        print(y0+y, x0+xs.min(), x0+xs.max(), xs.max()-xs.min()+1, ' '.join(f'{int(v):3d}' for v in row[max(xs.min()-3,0):xs.min()+4]), '|', ' '.join(f'{int(v):3d}' for v in row[xs.max()-3:xs.max()+4]))
cv2.imwrite(f'med_{v}.png',cv2.resize(a.astype(np.uint8),None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST))
