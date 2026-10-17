import numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p2/scripts')
from reg import *
np.set_printoptions(precision=2,suppress=True)
EA=((457.4,244.6),(865.0,254.9),100.1405,99.5206)
EC=((347.0,618.6),(593.4,684.1),175.3081,172.9881)
for conv in ['range','z']:
 for fA,pA in [(3401,18.7),(3460,18.7),(3517,18.7),(3460,17.7),(3460,19.7)]:
  for fC,pC in [(3800,53.0),(3870,53.0),(3950,53.0),(3870,51.0),(3870,55.0)]:
   for org in ['hull','aabb']:
    bA=((616.6,585.2),(616.6-155.43,585.2-6.03)) if org=='hull' else ((611.5,480),(611.5-155.43,480-6.03))
    bC=((359.2,925.3),(359.2-85.73,925.3-24.81)) if org=='hull' else ((357,900),(357-85.73,900-24.81))
    A=Reg(fA,480,480,pA,*bA,90.1103,90.4360,conv); C=Reg(fC,540,540,pC,*bC,173.7093,174.5515,conv)
    ea1=A.obj_W(EA[0],EA[2]); ea2=A.obj_W(EA[1],EA[3]); ec1=C.obj_W(EC[0],EC[2]); ec2=C.obj_W(EC[1],EC[3])
    print(conv,fA,pA,fC,pC,org,'| eagleA t1',ea1,'t2',ea2,'| eagleC t1',ec1,'t2',ec2,'| diff t1',ec1-ea1,'| camA',A.cam_W(),'camC',C.cam_W())
