import cv2, numpy as np, sys
v=sys.argv[1]; out=sys.argv[2]; frames=[int(x) for x in sys.argv[3].split(',')]
y0,y1,x0,x1=[int(x) for x in sys.argv[4].split(',')]
ims=[]
for k in frames:
    im=cv2.imread(f'frames/{v}/f{k:02d}.png')[y0:y1,x0:x1].copy()
    cv2.putText(im,str(k),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    ims.append(im)
cols=int(sys.argv[5]) if len(sys.argv)>5 else 4
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)]
cv2.imwrite(out,np.vstack(rows))
