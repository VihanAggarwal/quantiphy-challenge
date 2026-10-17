from util import *
fr=frames('internet_0010_segmented')
n=len(fr)
for i in range(0,n,3):
    f=fr[i].astype(np.int32)
    m=(f.min(axis=2)<200).astype(np.uint8)   # non-white
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    bl=sorted([(st[q,4],st[q,0],st[q,1],st[q,2],st[q,3],cen[q][0],cen[q][1]) for q in range(1,nl) if st[q,4]>15],reverse=True)
    print(i,' | '.join('A%d x%d y%d w%d h%d c(%.1f,%.1f)'%b for b in bl[:3]))
