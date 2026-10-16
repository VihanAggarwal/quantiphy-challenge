import cv2,numpy as np
src='captured_0014s'
bgf=cv2.imread('frames/%s_40.png'%src).astype(np.float32)
# board mask: bright, low saturation in bg frame
b=bgf
board=((b.min(2)>200)&((b.max(2)-b.min(2))<30))
board[:290]=0; board[440:]=0; board[:, :490]=0; board[:,620:]=0
board=cv2.erode(board.astype(np.uint8),np.ones((5,5),np.uint8))
ys,xs=np.nonzero(board); print('board bbox',xs.min(),xs.max(),ys.min(),ys.max())
cv2.imwrite('board_mask.png',board*255)
for i in range(9,19):
    f=cv2.imread('frames/%s_%02d.png'%(src,i)).astype(np.float32)
    d=np.abs(f-bgf).sum(2)*board
    m=d>30
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    yy,xx=np.nonzero(lab==k); w8=d[yy,xx]
    # also R-B beige measure
    rb=(f[:,:,2]-f[:,:,0])*board
    print(i,'bbox',x,y,w,h,'area',a,'cen %.1f %.1f'%(xx.mean(),yy.mean()),'wcen %.1f %.1f'%((xx*w8).sum()/w8.sum(),(yy*w8).sum()/w8.sum()),'bbox-mid %.1f %.1f'%(x+w/2-.5,y+h/2-.5))
