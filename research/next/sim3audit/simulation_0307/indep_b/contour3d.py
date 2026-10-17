import numpy as np, cv2
from sweep import to3d
from frame3d import axes
R=np.load('contour_sweep.npy')
f=3590; vzf=18.49/24
V,S,U=axes(f)
XL=to3d((1378,821),0.008866,f,vzf)[0]; XR=to3d((1950,712),0.008146,f,vzf)[0]; ref=(XL+XR)/2
out=[]
for x,y,q3,c3,q5,c5 in R:
    agree=abs(q3-q5)<0.00012
    q=(q3+q5)/2
    X=to3d((x,y),q,f,vzf)[0]-ref
    out.append((x,y,X@V,X@S,X@U,q3,q5,c3,c5,agree))
O=np.array(out)
ok=(O[:,9]>0)&(O[:,7]<0.3)
print('agree&lowcost',ok.sum(),'of',len(O))
o=np.argsort(O[ok,2]); A=O[ok][o]
print('REAR-most:'); [print('  px(%d,%d) fore %.2f span %.2f up %.2f q3 %.5f q5 %.5f c %.2f %.2f'%tuple(a[:9])) for a in A[:12]]
print('FRONT-most:'); [print('  px(%d,%d) fore %.2f span %.2f up %.2f q3 %.5f q5 %.5f c %.2f %.2f'%tuple(a[:9])) for a in A[::-1][:12]]
o=np.argsort(O[ok,3]); A=O[ok][o]
print('LEFT-most:'); [print('  px(%d,%d) fore %.2f span %.2f up %.2f'%tuple(a[:5])) for a in A[:5]]
print('RIGHT-most:'); [print('  px(%d,%d) fore %.2f span %.2f up %.2f'%tuple(a[:5])) for a in A[::-1][:5]]
np.save('contour3d.npy',O)
# overlay
from load import frames
img=frames('0305')[1].copy()
for a in O:
    col=(0,200,0) if (a[9]>0 and a[7]<0.3) else (0,0,255)
    cv2.circle(img,(int(a[0]),int(a[1])),2,col,-1)
    if a[9]>0 and a[7]<0.3: cv2.putText(img,'%d'%round(a[2]),(int(a[0])+3,int(a[1])),cv2.FONT_HERSHEY_PLAIN,0.7,(255,0,0),1)
cv2.imwrite('fr/contour_fore.png',cv2.resize(img[690:1010,1320:2010],None,fx=1.8,fy=1.8))
