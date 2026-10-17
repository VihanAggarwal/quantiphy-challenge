import cv2,numpy as np,sys
# track the black cat: dark pixels below ground; use median background subtraction
v=sys.argv[1]; roi=eval(sys.argv[2]) if len(sys.argv)>2 else None
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
frs=[]
while True:
    ok,f=c.read()
    if not ok: break
    frs.append(f)
seg='segmented' in v
res=[]
for i,f in enumerate(frs):
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    x0,y0,x1,y1=roi
    sub=g[y0:y1,x0:x1]
    m=(sub<45).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append(None); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    res.append((i,x+x0,y+y0,w,h,a,cen[k][0]+x0,cen[k][1]+y0))
for r in res: print(r)
r=np.array([r for r in res if r is not None],float)
p=np.polyfit(r[:,0],r[:,6],1); print('centroid px/frame',p[0], 'left',np.polyfit(r[:,0],r[:,1],1)[0],'right',np.polyfit(r[:,0],r[:,1]+r[:,3],1)[0])
print('median w,h',np.median(r[:,3]),np.median(r[:,4]),'max w',r[:,3].max())
