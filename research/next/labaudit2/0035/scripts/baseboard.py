import sys
from common import *
t=sys.argv[1]
med=cv2.imread(f'{OUT}/frames/{t}_median.png').astype(float).mean(2)
med=cv2.GaussianBlur(med,(5,5),1.5)
def scan(xs,y_guess,win=25):
    pts=[]
    for x in xs:
        col=med[:,x]
        y0=int(y_guess(x))
        seg=col[y0-win:y0+win]
        # darkest point = baseboard centre; lower edge = max positive gradient below it
        yd=y0-win+int(np.argmin(seg))
        g=np.diff(col[yd:yd+20])
        ylow=yd+int(np.argmax(g))+0.5
        gu=np.diff(col[yd-20:yd])
        yup=yd-20+int(np.argmin(gu))+0.5
        pts.append((x,yd,ylow,yup,col[yd]))
    return np.array(pts)
if t=='b':
    R=scan(list(range(640,820,10))+list(range(980,1270,10)),lambda x:185+(x-600)*(135/680))
    L=scan(range(270,590,10),lambda x:185+(600-x)*(190/350))
    for nm,P in [('right',R),('left',L)]:
        for col in [1,2,3]:
            A=np.vstack([P[:,0],np.ones(len(P))]).T
            c,res,_,_=np.linalg.lstsq(A,P[:,col],rcond=None)
            r=P[:,col]-A@c
            print(nm,['dark','lower','upper'][col-1],'y=%.4f x + %.2f'%tuple(c),'rms %.2f'%np.sqrt((r**2).mean()))
        print(np.round(P[:,:4],1).tolist())
