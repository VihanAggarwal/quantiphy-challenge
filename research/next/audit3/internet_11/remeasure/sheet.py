import cv2, numpy as np, sys
p=sys.argv[1]; out=sys.argv[2]; idx=[int(x) for x in sys.argv[3].split(',')]
c=cv2.VideoCapture(p); fr=[]
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in idx:
        f=cv2.resize(f,(640,360)); cv2.putText(f,str(i),(10,30),0,1,(0,255,255),2); fr.append(f)
    i+=1
while len(fr)%3: fr.append(np.zeros_like(fr[0]))
rows=[np.hstack(fr[k:k+3]) for k in range(0,len(fr),3)]
cv2.imwrite(out,np.vstack(rows))
