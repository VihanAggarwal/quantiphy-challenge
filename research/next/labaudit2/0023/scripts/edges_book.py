# subpixel edge extraction of the book cover on slope (frames 0-20 avg) and on table (frames 38-48 avg)
import numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
def cross(prof, y0, lo_val, hi_val, start, stop, step=1):
    """first subpixel crossing of mid level between lo_val and hi_val scanning from start to stop"""
    mid=0.5*(lo_val+hi_val)
    rng=range(start,stop,step)
    prev=None
    for y in rng:
        v=prof[y-y0]
        if prev is not None and (prev-mid)*(v-mid)<=0 and prev!=v:
            return (y-step)+step*(mid-prev)/(v-prev)
        prev=v
    return np.nan
out={}
for V in ['captured_0023x','captured_0023','captured_0023s']:
    for ph in ['slope','table']:
        A=np.load(D+f'frames/avg_{V}_{ph}.npy')  # y offset 300, x offset 400
        lum=A.mean(-1)  # simple gray
        rows=[]
        xs=range(548,646,4) if ph=='slope' else range(512,640,4)
        for x in xs:
            p=lum[:,x-400-1:x-400+2].mean(1)
            if ph=='slope':
                # cover level = median of rows 355-372
                cov=np.median(p[355-300:372-300])
                # back edge: scan downward from 335 to 360: background -> cover
                bg=np.median(p[330-300:340-300]) if V!='captured_0023' else np.median(p[338-300:344-300])
                yb=cross(p,300,bg,cov,335,362)
                # front edge: scan downward from 372 to 386: cover -> dark (min in 378..384)
                dmin=p[376-300:386-300].min()
                yf=cross(p,300,cov,dmin,372,386)
                # bottom: dark min in 384..392 -> board white below
                dmin2=p[384-300:392-300].min(); wb=np.median(p[391-300:398-300])
                ybot=cross(p,300,dmin2,wb,int(384+np.argmin(p[384-300:392-300])),400)
                rows.append((x,yb,yf,ybot))
            else:
                cov=np.median(p[484-300:490-300]) if x<600 else np.median(p[482-300:488-300])
                above=np.median(p[466-300:474-300])
                yb=cross(p,300,above,cov,470,490)
                dmin=p[490-300:502-300].min()
                yf=cross(p,300,cov,dmin,486,502)
                i2=int(np.argmin(p[503-300:516-300]))+503
                tab=np.median(p[516-300:522-300])
                ybot=cross(p,300,p[i2-300],tab,i2,525)
                rows.append((x,yb,yf,ybot))
        rows=np.array(rows)
        out[f'{V}_{ph}']=rows.tolist()
        print(V,ph,'n',len(rows))
        print('   x    back   front  bottom  cover_px  face_px')
        for r in rows[::3]: print('  %4d %7.2f %7.2f %7.2f %6.2f %6.2f'%(r[0],r[1],r[2],r[3],r[2]-r[1],r[3]-r[2]))
        print('  median cover px %.2f  face px %.2f'%(np.nanmedian(rows[:,2]-rows[:,1]),np.nanmedian(rows[:,3]-rows[:,2])))
json.dump(out,open(D+'scripts/book_edges.json','w'))
