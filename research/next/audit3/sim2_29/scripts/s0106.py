from util import *
fr=frames('simulation_0106',gray=True)
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(51,51))
res={}
for i in sorted(fr):
    m=(fr[i]<120).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,k)
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    bl=sorted([(cen[j][0],cen[j][1],np.sqrt(st[j,4]/np.pi)) for j in range(1,nl) if st[j,4]>5000])
    res[i]=bl
for i in [0,1,2,12,23,24,25,36,47,48,49]:
    print(i, ['(%.1f,%.1f r%.1f)'%b for b in res[i]])
def d(i):
    a,b=res[i]; return np.hypot(a[0]-b[0],a[1]-b[1])
print('sep24',d(24),'sep48',d(48))
# right virus pixel speed around frames
R=np.array([res[i][1][:2] for i in range(1,30) if len(res[i])==2])
L=np.array([res[i][0][:2] for i in range(1,30) if len(res[i])==2])
print('R speed per frame', np.hypot(*(R[-1]-R[0]))/(len(R)-1), 'L', np.hypot(*(L[-1]-L[0]))/(len(L)-1))
