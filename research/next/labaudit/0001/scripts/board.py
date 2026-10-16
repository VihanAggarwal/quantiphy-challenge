import cv2, numpy as np
base='/home/user/quantiphy-challenge/research/next/labaudit/0001/'
im=cv2.imread(base+'frames/f48.png').astype(float)
R=im[...,2]; G=im[...,1]; Bc=im[...,0]
m=((R>230)).astype(np.uint8)
m[:340]=0; m[510:]=0; m[:, :500]=0; m[:, 780:]=0
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); print(st[k])
B=(lab==k)
cv2.imwrite(base+'boardmask.png',(B*255).astype(np.uint8)[330:520,500:780])
L=[];Rr=[]
for y in range(350,500,4):
    xs=np.nonzero(B[y])[0]
    if len(xs): print(y, xs.min(), xs.max(), xs.max()-xs.min())
for x in range(560,740,15):
    ys=np.nonzero(B[:,x])[0]
    if len(ys): print('col',x, ys.min(), ys.max())
