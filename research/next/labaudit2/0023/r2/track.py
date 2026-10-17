import cv2, numpy as np, json
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
def cover_mask(im):
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV).astype(int)
    m=((hsv[...,0]>=82)&(hsv[...,0]<=108)&(hsv[...,1]>=22)&(hsv[...,2]>=140)).astype(np.uint8)
    m[:300]=0; m[560:]=0; m[:, :400]=0; m[:, 800:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: return m*0
    k=1+np.argmax(st[1:,4]); return (lab==k).astype(np.uint8)
def main():
  out={}
  for pre in ['o','s','x']:
      T=[]
      for i in range(0,49):
          im=cv2.imread(R1+f'{pre}{i:02d}.png')
          m=cover_mask(im); ys,xs=np.nonzero(m)
          if len(xs)==0: T.append(None); continue
          T.append(dict(i=i,area=int(len(xs)),cx=float(xs.mean()),cy=float(ys.mean()),x0=int(xs.min()),x1=int(xs.max()),y0=int(ys.min()),y1=int(ys.max()),
                        bx=float((xs.min()+xs.max())/2),by=float((ys.min()+ys.max())/2)))
      out[pre]=T
  json.dump(out,open('cover_track.json','w'))
  for i in range(16,33):
      s=' | '.join('%s a%5d c(%6.1f,%6.1f) bb x%3d-%3d y%3d-%3d'%(p,out[p][i]['area'],out[p][i]['cx'],out[p][i]['cy'],out[p][i]['x0'],out[p][i]['x1'],out[p][i]['y0'],out[p][i]['y1']) for p in 'osx')
      print(i,s)

if __name__=='__main__': main()
