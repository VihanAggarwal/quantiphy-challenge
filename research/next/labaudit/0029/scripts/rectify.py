import numpy as np, cv2
C=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0029/scripts/corners.npy')  # BL BR FR FL
for f in [690,700,711,720,740]:
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    sq=np.array([[0,0],[1,0],[1,1],[0,1]],float)
    H,_=cv2.findHomography(sq,C)
    M=np.linalg.inv(K)@H
    a1,a2,a3=M[:,0],M[:,1],M[:,2]
    ratio=np.linalg.norm(a1)/np.linalg.norm(a2)
    cosang=a1@a2/np.linalg.norm(a1)/np.linalg.norm(a2)
    print(f,'W/D=%.4f'%ratio,'cos=%.4f'%cosang)
