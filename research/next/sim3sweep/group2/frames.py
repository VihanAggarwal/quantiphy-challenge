import cv2,sys,os
vid=sys.argv[1]; idxs=[int(x) for x in sys.argv[2].split(',')]; scale=float(sys.argv[3]) if len(sys.argv)>3 else 0.5
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%vid)
n=0; frames={}
while True:
    ok,f=c.read()
    if not ok: break
    if n in idxs:
        g=cv2.resize(f,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
        cv2.imwrite('png/%s_f%03d.png'%(vid,n),g)
    n+=1
print(vid,'frames read',n)
