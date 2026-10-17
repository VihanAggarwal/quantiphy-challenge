import numpy as np
cx,cy=960.0,383.0
corners={'FL':(1104,387.3),'FR':(1420.7,410),'BR':(1467.3,349.3),'BL':(1186,328.7)}
for f in (1735,1780,1830,1860):
  for yh in (-70,):
    pitch=np.arctan((cy-yh)/f)   # down
    c,s=np.cos(pitch),np.sin(pitch)
    def bp(x,y):
        d=np.array([(x-cx)/f,(y-cy)/f,1.0])
        # camera->world: world Y down component: rotate by pitch about x (camera looks down)
        # world: X right, Yd = downward, Zf = forward horizontal
        yd = d[1]*c + d[2]*s
        zf = -d[1]*s + d[2]*c
        t = 1.0/yd   # plane at unit depth below camera
        return np.array([d[0]*t, zf*t])
    P={k:bp(*v) for k,v in corners.items()}
    L=lambda a,b: np.linalg.norm(P[a]-P[b])
    sides=[L('FL','FR'),L('FR','BR'),L('BR','BL'),L('BL','FL')]
    v1=P['FR']-P['FL']; v2=P['BL']-P['FL']
    ang=np.degrees(np.arccos(v1@v2/np.linalg.norm(v1)/np.linalg.norm(v2)))
    print('f',f,'pitch %.1f'%np.degrees(pitch),'sides/D',np.round(sides,3),'corner FL angle %.1f'%ang, 'mean %.3f'%np.mean(sides))
