# Backstep: Study #1 (NASA Glenn Research Center, WIND validation archive)

Source: https://www.grc.nasa.gov/WWW/wind/valid/backstep/backstep01/backstep01.html
(created 1998-12-11 by Dennis A. Yoder; last updated 2021-02-10). Text reproduced for
offline reference; figures omitted.

## Introduction

This study focuses on the incompressible flow over a backward-facing step, measured
experimentally by Driver & Seegmiller. This geometry has a step height to tunnel exit
height ratio of 1:9 which helps to minimize the freestream pressure gradient due to sudden
expansion. The experimental configuration also had a step height to tunnel width ratio of
1:12 to minimize three-dimensional effects. Data from the original experimentors is listed
in the file bstepdata.txt. All calculations presented below are for the case of zero degree
divergence of the top wall and were computed using a two-dimensional grid.

## Grid

A 238 x 185 single-zone mesh was generated to model the region from x/H = -105 to +50. The
grid was clustered to the solid surfaces such that y+ = 1. Downstream of the step, 55 points
were used in the recirculation region with ten of them placed within y+ = 30. The grid was
also clustered in the streamwise direction near the recirculation region to improve
resolution.

This grid is provided in Plot3d (two-dimensional, multiple-grid, unformatted, whole) and
common file format. The coordinates in both files are in units of feet and the step height
H is 0.5 inches.

## Boundary Conditions

Since this flow was modeled using a single zone, the step itself was modeled using a viscous
wall fringe boundary around a hole. Downstream of the step, the J1 boundary was also set to
viscous wall. On the Jmax boundary, the first 12 grid points were treated as an inviscid
wall in order to try and match the boundary layer profile at x/H = -4. The remainder of this
boundary was modeled using the viscous wall condition. The I1 boundary from J = 55 to 185
was set to an arbitrary inflow, and the Imax plane was set to a confined outflow.

## Comparisons of the Results

All of the velocity profiles are normalized by the flow velocity just before the backstep
(Uref = 44.2 m/s). The table below lists the reattachment location predicted by each model.

| Model | x_r / H |
| --- | --- |
| NPARC k-e | 5.31 |
| WIND k-e | 5.30 |
| WIND k-e Var. C | 5.55 |
| WIND SST | 6.43 |
| Experiment | 6.26 |

## References

Driver, D.M. and Seegmiller, H.L., "Features of a Reattaching Turbulent Shear Layer in
Divergent Channel Flow," AIAA Journal, Vol. 23, No. 2, Feb. 1985, pp. 163-171.

Yoder, Dennis A., and Georgiadis, Nicholas J., "Implementation and Validation of the Chien
k-epsilon Turbulence Model in the WIND Navier-Stokes Code," AIAA Paper 99-0745, Jan. 1999.
