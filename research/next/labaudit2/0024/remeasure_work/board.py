import cv2,numpy as np
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
def board_lines(img,verbose=True):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(int)
    m=(hsv[...,1]<45)&(hsv[...,2]>190)
    m[:340]=0;m[500:]=0;m[:,:590]=0;m[:,:600]=0;m[:,880:]=0
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    def fitpts(P):
        P=np.array(P,float)
        for it in range(3):
            # fit x = a y + b or y = a x + b depending on orientation
            mean=P.mean(0); U,S,Vt=np.linalg.svd(P-mean); d=Vt[0]; n=np.array([-d[1],d[0]])
            r=(P-mean)@n
            keep=np.abs(r)<max(1.0,2.5*np.std(r))
            P=P[keep]
        return mean,d,np.abs(r).max()
    top=[(x,340+np.where(m[340:430,x])[0].min()) for x in range(770,846) if m[340:430,x].any()]
    left=[(600+np.where(m[y,600:800])[0].min(),y) for y in range(372,458) if m[y,600:800].any()]
    right=[(700+np.where(m[y,700:880])[0].max(),y) for y in range(372,420) if m[y,700:880].any()]
    bot=[(x,430+np.where(m[430:500,x])[0].max()) for x in range(625,695) if m[430:500,x].any()]
    L={k:fitpts(v) for k,v in dict(top=top,left=left,right=right,bot=bot).items()}
    def inter(a,b):
        (p1,d1,_),(p2,d2,_)=L[a],L[b]
        A=np.stack([d1,-d2],1); t=np.linalg.solve(A,p2-p1); return p1+t[0]*d1
    C=dict(HL=inter('top','left'),HR=inter('top','right'),LR=inter('bot','right'),LL=inter('bot','left'))
    if verbose:
        for k,v in L.items(): print(k,'dir',np.round(v[1],4),'maxres',round(v[2],2))
        for k,v in C.items(): print(k,np.round(v,1))
    return C,L
if __name__=='__main__':
    for v in ['captured_0024x','captured_0024s','captured_0024']:
        print(v); board_lines(cv2.imread(f'{W}/{v}_medB.png'))
