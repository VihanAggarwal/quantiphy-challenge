from util import *
fr=frames('internet_0025_segmented')
H=[]
for i in range(0,305,15):
    f=fr[i].astype(np.int32); m=(f.min(axis=2)<200)
    xs=np.where(m.any(axis=0))[0]; x0=xs.min()
    # boatman columns: x0+15 .. x0+40, rows above 437
    sub=m[380:445, x0+15:x0+40]
    rows=np.where(sub.any(axis=1))[0]+380
    top=rows.min()
    # hull top at stern (column x0+3)
    hull=np.where(m[:,x0+3])[0].min()
    # width of person rows
    H.append((i,top,hull,hull-top))
for h in H: print(h)
print('median person top->hull-top',np.median([h[3] for h in H]))
