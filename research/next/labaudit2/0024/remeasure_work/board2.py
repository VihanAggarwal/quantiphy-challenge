import cv2,numpy as np
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
def mask(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(int)
    return (hsv[...,1]<45)&(hsv[...,2]>190)
def fitpts(P):
    P=np.array(P,float)
    for it in range(3):
        mean=P.mean(0); U,S,Vt=np.linalg.svd(P-mean); d=Vt[0]; n=np.array([-d[1],d[0]])
        r=(P-mean)@n; keep=np.abs(r)<max(1.0,2.5*np.std(r)); P=P[keep]
    return mean,d
def inter(l1,l2):
    (p1,d1),(p2,d2)=l1,l2
    t=np.linalg.solve(np.stack([d1,-d2],1),p2-p1); return p1+t[0]*d1
def corners(v):
    A=mask(cv2.imread(f'{W}/{v}_medA.png')); B=mask(cv2.imread(f'{W}/{v}_medB.png'))
    top=fitpts([(x,340+np.where(B[340:430,x])[0].min()) for x in range(770,846)])
    left=fitpts([(600+np.where(B[y,600:800])[0].min(),y) for y in range(372,464)])
    leftA=fitpts([(600+np.where(A[y,600:800])[0].min(),y) for y in range(400,464)])
    right=fitpts([(700+np.where(B[y,700:880])[0].max(),y) for y in range(372,420)])
    rightA=fitpts([(700+np.where(A[y,700:880])[0].max(),y) for y in range(372,420)])
    bot=fitpts([(x,430+np.where(A[430:500,x])[0].max()) for x in range(616,700)])
    C=dict(HL=inter(top,left),HR=inter(top,right),LR=inter(bot,right),LL=inter(bot,left))
    print(v,{k:np.round(c,1) for k,c in C.items()})
    print('  left dir B',np.round(left[1],4),'A',np.round(leftA[1],4),' right dir B',np.round(right[1],4),'A',np.round(rightA[1],4))
    print('  left x at y=440: B %.1f A %.1f ; right x at y=400: B %.1f A %.1f'%(
        left[0][0]+(440-left[0][1])*left[1][0]/left[1][1], leftA[0][0]+(440-leftA[0][1])*leftA[1][0]/leftA[1][1],
        right[0][0]+(400-right[0][1])*right[1][0]/right[1][1], rightA[0][0]+(400-rightA[0][1])*rightA[1][0]/rightA[1][1]))
    return C
if __name__=='__main__':
    for v in ['captured_0024x','captured_0024s','captured_0024']: corners(v)
