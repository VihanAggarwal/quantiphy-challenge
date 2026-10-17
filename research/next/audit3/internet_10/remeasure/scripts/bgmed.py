import cv2, numpy as np
W='research/next/audit3/internet_10/remeasure/'
sh=np.loadtxt(W+'shifts_clean.txt'); dx=(sh[:,0]+sh[:,2])/2; dy=(sh[:,1]+sh[:,3])/2
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
st=[]
for i in range(0,94,5):
    c.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=c.read()
    M=np.float32([[1,0,-dx[i]],[0,1,-dy[i]]])
    g=cv2.warpAffine(f,M,(3840,2160),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)[380:1200]
    st.append(g)
bg=np.median(np.array(st),axis=0).astype(np.uint8)
cv2.imwrite('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg_380_1200.png',bg)
print(bg.shape)
