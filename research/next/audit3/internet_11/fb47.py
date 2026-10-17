import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0047.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,29); ok,im=cap.read()
g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
for (y0,y1) in [(150,400),(700,1000)]:
  for (x0,x1) in [(0,960),(960,1920),(300,1600)]:
    strip=g[y0:y1,x0:x1]
    # horizontal gradient energy -> board edges are vertical lines
    gx=np.abs(np.diff(strip,axis=1)).mean(axis=0)
    gx=gx-gx.mean()
    n=len(gx); F=np.abs(np.fft.rfft(gx*np.hanning(n),n=8192))
    fr=np.fft.rfftfreq(8192)
    sel=(fr>1/150)&(fr<1/25)
    k=np.argmax(F*sel); 
    top=np.argsort(-(F*sel))[:5]
    print((y0,y1),(x0,x1),'period px %.1f'%(1/fr[k]), [round(1/fr[t],1) for t in top])
# red lines: find columns with dark red in row band 600-1000
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
b,gg,r=[im[:,:,i].astype(int) for i in range(3)]
red=((r-gg)>40)&(r<160)&(gg<90)
for row in [450,550,650,800,950,1050]:
    xs=np.where(red[row])[0]
    # cluster
    if len(xs)==0: print(row,'none'); continue
    cl=np.split(xs,np.where(np.diff(xs)>5)[0]+1)
    print(row,[(int(c[0]),int(c[-1]),len(c)) for c in cl if len(c)>10])
white=(g>200)
for row in [450,550,650,800,950,1050]:
    xs=np.where((im[row].min(axis=1)>190))[0]
    cl=np.split(xs,np.where(np.diff(xs)>5)[0]+1) if len(xs) else []
    print('white',row,[(int(c[0]),int(c[-1]),len(c)) for c in cl if len(c)>15])
