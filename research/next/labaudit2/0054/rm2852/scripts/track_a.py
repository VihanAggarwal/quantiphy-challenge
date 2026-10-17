import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
a=np.load(S+'a.npy').astype(np.float32)
ax=np.load(S+'ax.npy')
bg=np.median(a,axis=0)
# rough positions from ax comps
comps=json.load(open(S+'comps_ax.json'))
out={}
for k in range(22,42):
    f=a[k]
    d=np.abs(f-bg).max(-1)
    hsv=cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2HSV)
    # ax foreground
    fx=ax[k].astype(np.int16)
    fgx=np.sqrt(((fx-np.array([0,252,0]))**2).sum(-1))>60
    # region: x 250-640, y 200-720
    R=np.zeros(d.shape,bool); R[200:720,250:640]=True
    yellow=(hsv[...,0]>20)&(hsv[...,0]<45)&(hsv[...,1]>90)&(d>25)&R
    pale=(d>22)&R&~yellow&(hsv[...,1]<90)
    res={}
    for name,m in [('tennis',yellow),('white',pale)]:
        m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
        cs=[(st[i,4],cen[i],st[i]) for i in range(1,n) if st[i,4]>=12]
        cs.sort(key=lambda z:-z[0])
        res[name]=[(int(c[0]),[round(float(c[1][0]),1),round(float(c[1][1]),1)],[int(v) for v in c[2][:4]]) for c in cs[:3]]
    out[k]=res
    print(k,'T',res['tennis'][:2],' W',res['white'][:3])
