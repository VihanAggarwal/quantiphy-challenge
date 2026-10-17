import cv2, sys
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]
scale=float(sys.argv[3]) if len(sys.argv)>3 else 0.5
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_%s.mp4'%vid)
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in frames:
        g=cv2.resize(f,None,fx=scale,fy=scale)
        cv2.putText(g,'%s f%d'%(vid,i),(10,30),0,1,(0,0,255),2)
        cv2.imwrite('v_%s_%d.png'%(vid,i),g)
    i+=1
