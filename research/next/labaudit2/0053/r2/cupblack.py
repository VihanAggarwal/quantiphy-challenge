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
al=np.clip(lum/180,0,1)
tops=[]
for y in range(0,y1-y0):
    row=lum[y]; xs=np.where(row>60)[0]
    if len(xs)>5:
        tops.append((y0+y, xs.min()+x0, xs.max()+x0, al[y].sum()))
for t in tops[:30]: print('row %d L %d R %d alphaW %.1f'%t)
print('...'); 
for t in tops[-12:]: print('row %d L %d R %d alphaW %.1f'%t)
