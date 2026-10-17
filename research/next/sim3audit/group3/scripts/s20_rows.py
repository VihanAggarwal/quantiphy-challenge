import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0020.mp4')
acc=None;n=0
for i in range(131):
    ok,f=c.read()
    if not ok: break
    if i in (0,10,20,40,60,80,100,128):
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float)
        acc=g if acc is None else acc+g; n+=1
g=acc/n
# columns to use: avoid person (x 770-850) and ball rest (270-320)
for name,cols in [('L',slice(330,560)),('M',slice(560,760)),('R',slice(870,1060)),('LL',slice(20,260))]:
    prof=g[:,cols].mean(1)
    d=np.diff(prof)
    print(name)
    for y in range(700,960):
        if abs(d[y])>2.0 and abs(d[y])>=abs(d[y-1]) and abs(d[y])>=abs(d[y+1]):
            print('   y=%d.5 d=%.1f prof=%.0f->%.0f'%(y,d[y],prof[y],prof[y+1]))
