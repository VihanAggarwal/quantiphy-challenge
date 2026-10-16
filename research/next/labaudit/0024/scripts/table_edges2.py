import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
im=cv2.imread(D+'frames/x00.png')
g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(float)
gs=cv2.GaussianBlur(g,(5,5),1.5)
# for front-left edge: sample along columns, find max |gradient| between top+5 and bottom-5 along direction normal
for x in range(430,640,15):
    col=gs[440:620,x]; m=col>25
    ys=np.where(m)[0]; t,b=ys[0],ys[-1]
    d=np.diff(col)
    seg=d[t+4:b-4]
    i=np.argmin(seg); print('FL x',x,'top',440+t,'bot',440+b,'boundary',440+t+4+i,round(seg[i],1))
for x in range(870,1100,15):
    col=gs[440:620,x]; m=col>25
    ys=np.where(m)[0]; t,b=ys[0],ys[-1]
    d=np.diff(col)
    seg=d[t+4:b-4]
    i=np.argmin(seg); j=np.argmax(seg); print('FR x',x,'top',440+t,'bot',440+b,'min',440+t+4+i,round(seg[i],1),'max',440+t+4+j,round(seg[j],1))
