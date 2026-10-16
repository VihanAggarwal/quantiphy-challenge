import cv2, numpy as np, sys
r=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; outp=sys.argv[3]
x0,x1,y0,y1=[int(v) for v in sys.argv[4].split(',')]
sc=float(sys.argv[5]) if len(sys.argv)>5 else 1.0
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/frames/'
ims=[]
for i in idx:
    im=cv2.imread(d+'%s_%02d.png'%(r,i))[y0:y1,x0:x1]
    im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    cv2.putText(im,str(i),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    ims.append(im)
nc=int(sys.argv[6]) if len(sys.argv)>6 else 3
while len(ims)%nc: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[k:k+nc]) for k in range(0,len(ims),nc)]
cv2.imwrite(outp,np.vstack(rows))
