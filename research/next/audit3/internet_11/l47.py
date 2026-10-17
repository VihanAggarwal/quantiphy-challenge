import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0047.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,29); ok,im=cap.read()
im=im.astype(int); b,g,r=im[:,:,0],im[:,:,1],im[:,:,2]
dark=(r+g+b)<200
wht=(b>180)&(g>180)
for row in [480,520,560,600,700,800,900,1000,1070]:
    def cl(mask):
        xs=np.where(mask[row])[0]
        if len(xs)==0: return []
        c=np.split(xs,np.where(np.diff(xs)>3)[0]+1)
        return [(int(a[0]),int(a[-1]),len(a)) for a in c if len(a)>15]
    print(row,'dark',cl(dark),'white',cl(wht))
# horizontal red line: rows dark at several columns
for col in [400,800,1200,1600]:
    ys=np.where(dark[:,col])[0]
    c=np.split(ys,np.where(np.diff(ys)>3)[0]+1) if len(ys) else []
    print('col',col,[(int(a[0]),int(a[-1]),len(a)) for a in c if len(a)>10])
