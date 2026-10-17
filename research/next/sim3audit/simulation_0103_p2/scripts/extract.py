import cv2, sys, os
# usage: extract.py clip frame1 frame2 ... ; writes frames/<clip>_fNNN.png
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
O='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/frames/'
clip=sys.argv[1]; fr=[int(x) for x in sys.argv[2:]]
c=cv2.VideoCapture(D+clip+'.mp4')
i=0
while True:
    ok,im=c.read()
    if not ok: break
    if i in fr:
        cv2.imwrite(O+f'{clip}_f{i:03d}.png',im)
    i+=1
print(clip,'n',i)
