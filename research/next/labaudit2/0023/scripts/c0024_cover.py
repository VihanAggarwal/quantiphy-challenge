import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
im=cv2.imread(D+'other/avg_0024x_slope.png').astype(np.float32)
B,G,R=im[...,0],im[...,1],im[...,2]
blue=((G-R)>14)&(G>120)
n,lab,st,cen=cv2.connectedComponentsWithStats(blue.astype(np.uint8))
k=1+np.argmax(st[1:,4]); m=(lab==k)
ys,xs=np.nonzero(m); print('cover bbox',xs.min(),xs.max(),ys.min(),ys.max(),'area',m.sum())
cv2.imwrite(D+'other/c0024_covermask.png',(m*255).astype(np.uint8)[330:420,690:870].repeat(4,0).repeat(4,1))
# boundary samples
top=[];bot=[]
for x in range(xs.min(),xs.max()+1):
    yy=np.nonzero(m[:,x])[0]
    if len(yy): top.append((x,yy.min()-0.5)); bot.append((x,yy.max()+0.5))
left=[];right=[]
for y in range(ys.min(),ys.max()+1):
    xx=np.nonzero(m[y])[0]
    if len(xx): left.append((y,xx.min()-0.5)); right.append((y,xx.max()+0.5))
top=np.array(top);bot=np.array(bot);left=np.array(left);right=np.array(right)
for nm,a in [('top',top),('bot',bot)]: print(nm,a[::8].tolist())
for nm,a in [('left',left),('right',right)]: print(nm,a[::3].tolist())
