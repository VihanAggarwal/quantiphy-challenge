import cv2,numpy as np
for src in ['captured_0014s','captured_0014x','captured_0014']:
    b=cv2.imread('frames/%s_40.png'%src).astype(np.float32)
    board=((b.min(2)>205)&((b.max(2)-b.min(2))<35)).astype(np.uint8)
    board[:280]=0; board[450:]=0; board[:, :480]=0; board[:,630:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(board)
    k=1+np.argmax(st[1:,4]); M=(lab==k).astype(np.uint8)
    M=cv2.morphologyEx(M,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    cnts,_=cv2.findContours(M,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea).reshape(-1,2).astype(float)
    # fit 4 lines: split contour points by side using min-area-rect-like approach: use approxPolyDP to get corners, then refit lines
    ap=cv2.approxPolyDP(c.astype(np.int32).reshape(-1,1,2),6,True).reshape(-1,2)
    print(src,'area',M.sum(),'approx',ap.tolist())
    if src=='captured_0014s': np.save('board_contour.npy',c); cv2.imwrite('board_mask_full.png',M*255)
