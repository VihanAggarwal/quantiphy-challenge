import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
ims=[cv2.imread(D+f'frames/x{i:02d}.png').astype(float) for i in range(40,49)]
im=np.median(np.stack(ims),0)
b,g,r=im[...,0],im[...,1],im[...,2]
# book pixels: bluish/neutral bright (teal top: b>r ; pages: bright cream: r,g,b all > 150 and r-b<40)
# table: brown r-b > 50
tealtop=(b-r>15)&(g>110)
pages=(r>150)&(g>150)&(b>130)&((r-b)<45)
book=(tealtop|pages)
rows=[]
for x in range(494,650,2):
    ys=np.where(book[440:520,x])[0]+440
    if len(ys)==0: continue
    tt=np.where(tealtop[440:520,x])[0]+440
    rows.append((x,ys.min(),ys.max(),tt.min() if len(tt) else -1,tt.max() if len(tt) else -1))
for rr in rows: print(rr)
cv2.imwrite(D+'book_rest_mask.png',cv2.resize((np.dstack([book*255,tealtop*255,pages*255])).astype(np.uint8)[440:520,480:680],None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST))
