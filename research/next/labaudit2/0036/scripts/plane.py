import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/'
im=cv2.imread(S+'captured_0036x/f45.png').astype(float)
# table mask: not near-white
m=(im.min(2)<200)
m[650:,:]=False
def fitline(pts):
    pts=np.array(pts,float); mu=pts.mean(0); _,_,vt=np.linalg.svd(pts-mu); d=vt[0]
    n=np.array([-d[1],d[0]]); return np.array([n[0],n[1],-n@mu])
def subx(y,side):
    row=im[y,:,:].min(1)  # min channel
    xs=np.where(row<200)[0]; xs=xs[(xs>150)&(xs<1100)]
    if side=='L':
        x=xs.min(); # subpixel crossing of 200 between x-1 and x
        a,b=row[x-1],row[x]; return x-1+(a-200)/(a-b)
    else:
        x=xs.max(); a,b=row[x],row[x+1]; return x+(a-200)/(a-b)
L=[(subx(y,'L'),y) for y in range(455,580)]
Rr=[(subx(y,'R'),y) for y in range(460,580)]
B=[]
for x in range(450,730):
    col=im[380:520,x,:].min(1); i=np.where(col<200)[0][0]; a,b=col[i-1],col[i]; B.append((x,380+i-1+(a-200)/(a-b)))
# front edge: in original render, boundary between top surface and darker front face
g=cv2.imread(S+'captured_0036/f45.png').astype(float).mean(2)
Fr=[]
for x in range(240,960,4):
    col=cv2.GaussianBlur(g[560:620,x-2:x+3],(0,0),0.7).mean(1)
    gr=np.diff(col); i=np.argmin(gr)  # strongest bright->dark going down
    Fr.append((x,560+i+0.5))
lines={}
for k,v in dict(L=L,R=Rr,B=B,F=Fr).items():
    l=fitline(v); lines[k]=l; v=np.array(v); res=v@l[:2]+l[2]
    print(k,'n=%d rms %.2f max %.2f'%(len(v),res.std(),abs(res).max()), 'ends',v[0],v[-1])
json.dump({k:list(map(float,v)) for k,v in lines.items()},open('scripts/lines.json','w'))
def X(a,b): p=np.cross(a,b); return p/p[2]
for f in [711.,766.]:
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); Ki=np.linalg.inv(K)
    vL=X(lines['L'],lines['R']); vF=X(lines['F'],lines['B'])
    d1=Ki@vL; d1/=np.linalg.norm(d1); d2=Ki@vF; d2/=np.linalg.norm(d2)
    if d1[2]<0: d1=-d1
    if d2[0]<0: d2=-d2
    ang=np.degrees(np.arccos(abs(d1@d2)))
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    if n[1]<0: n=-n
    print('f',f,'VP recede',vL[:2],'VP across',vF[:2],'angle %.1f'%ang,'normal',n.round(4))
    # orthogonalized: use d1 and n from both, also normal from d1 only + horizon assumption skip
    np.save(f'scripts/normal_{int(f)}.npy',n)
    corners={'FL':X(lines['F'],lines['L']),'FR':X(lines['F'],lines['R']),'BL':X(lines['B'],lines['L']),'BR':X(lines['B'],lines['R'])}
    print(' corners',{k:v[:2].round(1) for k,v in corners.items()})
    for h in [0.17,0.18,0.19]:
        P={k:(Ki@v)*h/(n@(Ki@v)) for k,v in corners.items()}
        fr=np.linalg.norm(P['FR']-P['FL']); bk=np.linalg.norm(P['BR']-P['BL']); le=np.linalg.norm(P['BL']-P['FL']); ri=np.linalg.norm(P['BR']-P['FR'])
        print('  h %.2f front %.3f back %.3f left %.3f right %.3f side/front %.3f'%(h,fr,bk,le,ri,(le+ri)/(fr+bk)))
