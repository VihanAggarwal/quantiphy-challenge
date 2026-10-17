import cv2,numpy as np,sys
W='/home/user/quantiphy-challenge/research/next/labaudit2/0024/remeasure_work'
v=sys.argv[1]
def mask(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(int); return (hsv[...,1]<40)&(hsv[...,2]>200)
A=mask(cv2.imread(f'{W}/{v}_medA.png')); B=mask(cv2.imread(f'{W}/{v}_medB.png'))
def fitpts(P):
    P=np.array(P,float)
    for it in range(3):
        mean=P.mean(0); U,S,Vt=np.linalg.svd(P-mean); d=Vt[0]; n=np.array([-d[1],d[0]])
        r=(P-mean)@n; keep=np.abs(r)<max(0.8,2.5*np.std(r)); P=P[keep]
    return mean,d,np.std(r)
def inter(l1,l2):
    t=np.linalg.solve(np.stack([l1[1],-l2[1]],1),l2[0]-l1[0]); return l1[0]+t[0]*l1[1]
top=fitpts([(x,330+np.where(B[330:420,x])[0].min()) for x in range(530,650)])
left=fitpts([(470+np.where(B[y,470:600])[0].min(),y) for y in range(372,468)])
right=fitpts([(600+np.where(B[y,600:720])[0].max(),y) for y in range(372,468)])
leftA=fitpts([(470+np.where(A[y,470:600])[0].min(),y) for y in range(392,468)])
rightA=fitpts([(600+np.where(A[y,600:720])[0].max(),y) for y in range(392,468)])
bot=fitpts([(x,440+np.where(A[440:520,x])[0].max()) for x in range(510,660)])
for k,l in dict(top=top,left=left,right=right,leftA=leftA,rightA=rightA,bot=bot).items(): print(k,np.round(l[0],1),np.round(l[1],4),'sd %.2f'%l[2])
C=[inter(bot,left),inter(bot,right),inter(top,right),inter(top,left)]
print('corners LL LR HR HL',[np.round(c,1) for c in C])
np.save(f'{W}/{v}_board.npy',np.array(C))
