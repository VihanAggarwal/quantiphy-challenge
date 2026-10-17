import cv2, sys
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0001.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
idx=[int(x) for x in sys.argv[1].split(',')]
scale=float(sys.argv[2]) if len(sys.argv)>2 else 0.5
for i in idx:
    im=cv2.resize(fr[i],None,fx=scale,fy=scale)
    cv2.putText(im,str(i),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    cv2.imwrite(f'f{i:02d}.png',im)
