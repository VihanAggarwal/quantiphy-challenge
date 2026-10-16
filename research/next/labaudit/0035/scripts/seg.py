import cv2, numpy as np, sys, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
def masks(f):
    b,g,r=[f[...,i].astype(int) for i in range(3)]
    green=((g>150)&(r<120)&(b<120)) | ((b>246)&(g>246)&(r>246))
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    orange=(~green)&(h>=3)&(h<=22)&(s>110)&(v>60)
    return green,orange
def comp_stats(m):
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8),8)
    return n,lab,st,cen
if __name__=='__main__':
    v=sys.argv[1]
    fr=np.load(f'{S}/f0035{v}.npy')
    out=[]
    for i,f in enumerate(fr):
        green,orange=masks(f)
        k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        o=cv2.morphologyEx(orange.astype(np.uint8),cv2.MORPH_OPEN,k)
        o=cv2.morphologyEx(o,cv2.MORPH_CLOSE,k)
        n,lab,st,cen=comp_stats(o)
        j=1+np.argmax(st[1:,4]) if n>1 else None
        if j is None: out.append(None); continue
        x,y,w,h,a=st[j]
        out.append(dict(i=i,cx=float(cen[j][0]),cy=float(cen[j][1]),w=int(w),h=int(h),A=int(a),deq=float(np.sqrt(4*a/np.pi))))
        print(i, '%.1f %.1f'%tuple(cen[j]), w,h,a,'%.1f'%np.sqrt(4*a/np.pi))
    json.dump(out,open(f'{S}/bb_{v}.json','w'))
