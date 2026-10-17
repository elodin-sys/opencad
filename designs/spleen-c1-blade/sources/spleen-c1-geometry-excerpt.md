# SPLEEN C1 high-speed low-pressure turbine cascade — geometry excerpts

Source: SPLEEN – High Speed Turbine Cascade – Test Case Database, version v5 (von Karman
Institute for Fluid Dynamics; Lavagnoli, Lopes, Simonassi, Torre), Zenodo record 13712768,
doi:10.5281/zenodo.13712768, CC-BY-4.0. Files quoted: `Test_Case_Setup/SPLEEN-HSTC-DB-
Geometry_TestSection_Info_v2.pdf` (Table 2.1) and `WARNING-README-HSTC-DB--UPDATELIST-v5.txt`.

## Table 2.1: Geometric parameters of the SPLEEN C1 cascade

| Parameter | SPLEEN C1 |
|---|---|
| Cascade true chord, c [mm] | 52.28 |
| Cascade axial chord, c_ax [mm] | 47.61 |
| Cascade pitch, g [mm] | 32.95 |
| Cascade span [mm] | 165.0 |
| TE radius [mm] | 0.435 |
| Throat opening, o [mm] | 19.40 |
| Inlet metal angle, α_in [deg] | 37.30 |
| Outlet metal angle, α_out [deg] | 53.80 |
| Stagger angle, σ [deg] | 24.40 |

"The blade span is 165 mm whereas the test section height upstream of the inlet boundary
layer lip is 225 mm."

## Coordinate file

`SPLEENC1_Geometry_Airfoil_2D_v1.xlsx`, sheet `SPLEENC1_Coord`: two header rows, then 1001
rows per side. Columns A–B are the pressure side (PS) x [m], y [m]; columns C–D are the
suction side (SS) x [m], y [m]. Both sides start at the leading edge, which is the origin
(0, 0), and end at the shared trailing-edge point (0.0476144 m, -0.0215997 m). Sheet
`Features` repeats the cascade parameters (stagger 24.4 deg, axial chord 47.614 mm, true
chord 52.285 mm, pitch 32.951 mm, TE radius 0.435 mm).

## Database update note (version 2, 25/11/2022)

"A mistake was found in the geometry of the SPLEEN C1 cascade contained in files
SPLEENC1_Geometry_Airfoil_2D_CAD_v1.igs / .stp / .x_t that were released in the first
version of the database SPLEEN-HSTC-DB_v1. In these files the geometry of the airfoil has a
wrong stagger angle. The SPLEEN C1 coordinates provided in the file
SPLEENC1_Geometry_Airfoil_2D_v1.xlsx is instead correct. PLEASE USE version 2 of the SPLEEN
C1 CAD files (SPLEENC1_Geometry_Airfoil_2D_CAD_v2) provided in the new versions of the
database."
