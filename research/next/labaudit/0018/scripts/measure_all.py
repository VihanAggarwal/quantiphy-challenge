"""captured_0018 family: static measurements (pixel readings taken by eye from gridded zooms, see ../grid_*.png)."""
from common import *
f=F
# --- pixel readings (full-res 1280x720, identical geometry in o/s/x renders: edge-correlation shift 0,0)
box_w_px, box_h_px = 20.0, 52.5          # held box (frames 0-28), x 470.2-490.0, y 239.7-292
box_uv = (480, 266)
box_floor_v = 585.0                      # box lands on its end, frames 41-43 (bottom 584-586)
ball_px, ball_uv = 45.0, (542, 265)      # soccer ball held, 44-45 px both axes
ball_floor_v = 575.0                     # soccer ball lowest bottom, frames 39-40 (blurred, 573-578)
ten_px, ten_floor_v, ten_u = 20.0, 614.0, 750   # tennis ball width 20 px; lowest blurred bottom frame 36
lfeet_v = 572.0                          # left person's near shoe, mid-sole contact (heel 571, toe 577)
L_top, L_bot = 173, 577                  # left person mask extent
R_top = 102                              # right person top (cap/hair)
toy_px = 55.0                            # pineapple incl. leaves y 221-276
rng_ball, rng_near, rng_far = 2.80, 2.002, 3.130
# --- floor height from the tennis ball (stated-elsewhere size 6.7 cm), zero pitch assumed
z_ten = f*0.067/ten_px
h = (ten_floor_v-360)*z_ten/f
print(f'tennis z at floor contact {z_ten:.3f} m -> camera height above floor h={h:.3f} m')
for nm,v in [('left feet',lfeet_v),('soccer contact',ball_floor_v),('box contact',box_floor_v)]:
    print(f'  floor z at {nm} (v={v}): {h*f/(v-360):.3f}')
zL_range = zfromrange(380,300,rng_far); zR_range = zfromrange(990,330,rng_near)
print(f'left person z: range-interp {zL_range:.3f}, z-interp {rng_far}; floor-model {h*f/(lfeet_v-360):.3f}')
h_feet = (lfeet_v-360)*zL_range/f
print(f'h from left feet at range-interp torso z: {h_feet:.3f}')
# --- box
z_ball_rng = zfromrange(*box_uv, rng_ball)
routes = {
 'R1 box at ball range 2.80 (occlusion: box in front of ball arm => upper bound)': z_ball_rng,
 'R1b ball range 2.80 is surface, centre +9cm': zfromrange(*box_uv, rng_ball+0.09),
 'R2 floor contact, h from tennis ball': h*f/(box_floor_v-360),
 'R2b floor contact, h from left feet (range interp)': h_feet*f/(box_floor_v-360),
 'R2c floor contact, h from left feet (z interp, upper bound)': (lfeet_v-360)*rng_far/f*f/(box_floor_v-360),
}
for k,z in routes.items():
    print(f'BOX {k}: z={z:.3f}  width={box_w_px*z/f*100:.2f} cm  length={box_h_px*z/f*100:.2f} cm')
print(f'BOX pixel aspect W/L={box_w_px/box_h_px:.3f}; x current length 21 -> width {21*box_w_px/box_h_px:.2f}')
# --- soccer ball
for nm,r in [('centre',rng_ball),('surface',rng_ball+0.09)]:
    z=zfromrange(*ball_uv,r); print(f'SOCCER diameter ({nm} range) {ball_px*z/f*100:.2f} cm')
zc=h*f/(ball_floor_v-360); print(f'SOCCER diameter at floor-contact z {zc:.3f}: {45.5*zc/f*100:.2f} cm')
# --- persons
for nm,z in [('range',zL_range),('z',rng_far),('floor',h*f/(lfeet_v-360))]:
    print(f'LEFT height ({nm} z={z:.3f}): {(L_bot-L_top)*z/f*100:.1f} cm')
for nm,z,hh in [('range',zR_range,h),('z',rng_near,h),('range,h_feet',zR_range,h_feet),('z,h_zfeet',rng_near,(lfeet_v-360)*rng_far/f)]:
    print(f'RIGHT height ({nm} z={z:.3f}, h={hh:.3f}): {((360-R_top)*z/f+hh)*100:.1f} cm')
PL=bp_range(380,300,rng_far); PR=bp_range(990,330,rng_near)
print(f'PEOPLE distance range-interp {np.linalg.norm(PL-PR)*100:.1f}; z-interp {np.linalg.norm(bp_z(380,300,rng_far)-bp_z(990,330,rng_near))*100:.1f}')
zf=lambda v: h*f/(v-360)
Lf=np.array([(385-640)/f*zf(572),zf(572)]); Rf=np.array([((995-640)/f*zf(715)+(940-640)/f*zf(668))/2,(zf(715)+zf(668))/2])
print(f'PEOPLE distance, feet on floor model: {np.linalg.norm(Lf-Rf)*100:.1f}')
# --- toy (pineapple) depth bracket: torso z (range) .. tennis-ball z held
z_ten_held=f*0.067/20.5
for z in [zR_range, 1.95, 2.05, z_ten_held]:
    print(f'TOY height at z={z:.3f}: {toy_px*z/f*100:.1f} cm')
# --- shoe (near shoe): heel (348, 571) toe (400, 577) on floor
for hh in [h,h_feet]:
    zh=hh*f/(571-360); zt=hh*f/(577-360)
    P1=np.array([(348-640)/f*zh,zh]); P2=np.array([(400-640)/f*zt,zt])
    zm=(zh+zt)/2
    print(f'SHOE h={hh:.3f}: floor-plane {np.linalg.norm(P1-P2)*100:.1f} cm; if parallel to image {52*zm/f*100:.1f} cm')
