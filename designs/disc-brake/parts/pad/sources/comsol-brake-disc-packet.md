# Heat generation in a disc brake: reference packet

Transcribed from the COMSOL Multiphysics 6.3 Application Library model *Heat Generation in a Disc Brake*
(`Heat_Transfer_Module/Thermal_Contact_and_Friction/brake_disc`, https://doc.comsol.com/6.3/doc/com.comsol.help.models.heat.brake_disc/brake_disc.html,
accessed 2026-09-25). This packet carries the model definition, geometry construction and physics settings. The results
section of the documentation is not included. Lengths in the documentation are metres; the contract works in millimetres.

## Scenario

An 1,800 kg car travels at 25 m/s until the driver panic-brakes for 2 seconds. The eight brake pads slow the car at
10 m/s² (no wheel skid). After two seconds of braking the brake is released and the car continues at 5 m/s for eight
seconds without braking. Questions: how hot the disc and pads get while braking, and how much they cool afterwards.
Braking power starts to fade above 600 K.

## Model definition

The disc is a 3D solid of radius 0.14 m and thickness 0.013 m (Figure 1). Heat conduction in the disc and the pad follows
the transient heat equation; the disc and pad surfaces lose heat to the surrounding air by convection and radiation.

Table 1: material properties.

| Property | Description | Disc | Pad | Air |
| --- | --- | --- | --- | --- |
| rho (kg/m3) | Density | 7870 | 2000 | 1.170 |
| Cp (J/(kg K)) | Heat capacity at constant pressure | 449 | 935 | 1100 |
| k (W/(m K)) | Thermal conductivity | 82 | 8.7 | 0.026 |
| epsilon | Surface emissivity | 0.28 | 0.8 | - |

After 2 s, contact is made at the interface between the disc and the pad. Neglecting drag and other losses outside the
brakes, the brakes' retardation power is the negative time derivative of the car's kinetic energy, P = -m v dv/dt, where
m is the car's mass (1800 kg) and v its speed (Figure 2: velocity profile; Figure 3: acceleration profile).

At one of the eight brakes the frictional heat source is

    P_b = P / 8 = -(1/8) m v dv/dt

The contact pressure between the disc and the pad is related to the frictional heat source per unit area, Q_b = P_b / A, by

    p = Q_b / (mu v),   with friction coefficient mu = 0.3.

The rotation is modelled as convection in the disc (a solid with translational motion). The local disc velocity vector is

    v_d = (v / R) (-y, x)          (R: the wheel radius, the model parameter r_wheel)

Produced and dissipated heat of the disc are recovered as W_prod = integral from 0 to t0 of Q_prod dt and
W_diss = integral from 0 to t0 of Q_diss dt, where Q_prod is the frictional heat rate at the contact and Q_diss the
convective plus radiative heat rate over all external surfaces.

## Global parameters

The documentation loads them from the Application Library file `brake_disc_parameters.txt`, which is not published on
the page. Names used in the settings below: `v0` (initial speed), `a0` (acceleration, negative), `t_brake_start`,
`t_brake_end`, `r_wheel` (wheel radius), `T_air` (air temperature), `m_car`, `mu`. Values stated in the text: m_car = 1800 kg,
v0 = 25 m/s, deceleration 10 m/s², braking from t = 2 s to t = 4 s, mu = 0.3. `r_wheel` and `T_air` are not stated.

## Geometry construction (units m)

1. Cylinder 1: radius 0.14, height 0.013 (base at z = 0).
2. Cylinder 2: radius 0.08, height 0.01, positioned at z = 0.013.
3. Work plane at z = 0.013 with four cubic Bezier curves (control points (xw, yw); unlisted coordinates are 0):
   - Cubic Bezier 1: (0, 0.135), (0.02, 0.135), (0.05, 0.13), (0.04, 0.105); weight of control point 3 = 2.5.
   - Cubic Bezier 2: (0.04, 0.105), (0.03, 0.08), (0.035, 0.09), (0, 0.09).
   - Cubic Bezier 3: (0, 0.09), (-0.035, 0.09), (-0.03, 0.08), (-0.04, 0.105).
   - Cubic Bezier 4: (-0.04, 0.105), (-0.05, 0.13), (-0.02, 0.135), (0, 0.135); weight of control point 2 = 2.5.
   - Convert to solid (the closed outline becomes a face).
4. Extrude the work plane outline by 0.0065.
Domains 1 and 2 (the two cylinders) are the disc; domain 3 (the extruded outline) is the pad. The disc's bottom face
(z = 0) is a symmetry plane: the model is half of a disc with a pad on each side.

## Physics settings

- Heat Transfer in Solids, time dependent. Solid with Translational Motion on the disc domains with
  u_trans = (-y v(t)/r_wheel, x v(t)/r_wheel, 0).
- Velocity v(t): piecewise, v0 until t_brake_start, v0 + a0 (t - t_brake_start) until t_brake_end, then constant
  (v0 + a0 (t_brake_end - t_brake_start)) to t = 12 s; smoothing with continuous second derivative, absolute transition
  zone 0.2 s. Acceleration a(t) = dv/dt.
- Heat Flux on all boundaries: convective heat flux, external forced convection with L = 0.14 m, U = v(t), external
  temperature T_air.
- Thermal Contact on the pad/disc interface (boundary 11): contact pressure p = Qb/(mu v(t)), microhardness Hc = 800 MPa,
  thermal friction by heat rate with P_b = -m_car v(t) a(t) / 8.
- Surface-to-ambient radiation: disc faces emissivity 0.28, pad faces emissivity 0.8, ambient temperature T_air.
- Symmetry on boundary 3 (the disc bottom, z = 0).
- Initial values: T = T_air.

## Mesh and study

Free triangular mesh (extra fine) on boundaries 4, 7 and 11, swept through the thickness with 2 elements; about 5,800
elements in total. Time dependent study, output times 0:0.5:1.5, 1.55:0.05:3, 3.2:0.2:5, 6:1:12 s, relative tolerance
0.005, intermediate time stepping.

## Result probe

A radial cut line at the disc surface (z = 0.0129) from (0, 0, 0.0129) to (-0.047, 0.1316, 0.0129) (Figure 5) is used to
plot temperature against time along the radius.
