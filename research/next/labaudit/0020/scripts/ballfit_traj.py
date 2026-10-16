import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0020/scripts')
import numpy as np, ballfit as B
jarF=list(range(15,28)); toyF=[14,15,16,17,19,20,21,22,23,24]
for fps in (24.,25.):
  for obj,fr,rng in (('jar',jarF,1.9735),('toy',toyF,2.63)):
    for wr in (0,5):
      p,rms,_=B.fit(obj,fr,'x',rng=rng,w_r=wr,fps=fps)
      fs=np.arange(12,29)
      P=B.model(p,fs/fps,B.down)
      rr=np.linalg.norm(P,axis=1)
      print('fps',fps,obj,'wr',wr,'rms %.2f'%rms,' '.join('f%d:%.2f'%(f,r) for f,r in zip(fs,rr)))
      # forward-difference velocity at frame round(0.6*fps) and displacement frames
      f0=0.6*fps; f1=0.8*fps
      Pa=B.model(p,np.array([f0,f0+1,f1])/fps,B.down)
      print('    fwd-diff v at 0.6: %.1f cm/s ; disp 0.6-0.8 %.1f cm'%(np.linalg.norm(Pa[1]-Pa[0])*fps*100,np.linalg.norm(Pa[2]-Pa[0])*100))
