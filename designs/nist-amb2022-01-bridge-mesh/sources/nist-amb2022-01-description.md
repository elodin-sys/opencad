# AMB2022-01 Benchmark Measurements and Challenge Problems — geometry excerpts

Source: NIST AM Bench, https://www.nist.gov/ambench/amb2022-01-benchmark-measurements-and-challenge-problems
(page inspected 2026-09-15). Excerpts limited to the sections that describe the individual bridge
part's geometry; figures referenced below are supplied as separate image files (Figure 3 is the
dimensioned drawing, updated by NIST on 2023-09-20; Figure 4 shows leg numbering and the L10
thin-wall scan pattern). Units are millimetres.

## 1. Overview and Basic Objectives

The AMB2022-01 benchmarks use laser powder bed fusion (LPBF) 3D metal alloy builds of a bridge
structure geometry that has 12 legs of varying size, as shown in Figure 1. All of the legs are solid
except for leg 10 that is hollow with thin internal walls.

## 2.1.3 Individual part geometry

Figure 3 presents a schematic of the bridge structure part that is 75 mm long, 12 mm tall, and 5 mm
wide with 7 mm tall 'legs' that form into 45° overhangs below a solid structure. The recoating
direction starts at the pointed end with the 45° taper, and proceeds left. CAD geometry of the entire
build with 6 parts, or individual bridge-structure or recoater guide structures are available as STEP
or STL geometry files in the \CAD_Geometry\ directory of the AMB2022-01 challenge description dataset.

Figure 3: Plan (top) and elevation (bottom) views of the AMB2022-01 bridge structure external
geometry.

Leg L10 of each as-built part has a hollow cavity with four thin-wall structures shown in Figure 4.
The outer walls of the L10 leg are approximately 0.5 mm thick and enclose two thin walls that are the
width of a single laser track and another two that are the width of a double laser track. The thin
walls are aligned parallel to the recoater blade direction. The bottoms of the walls sit on a solid
base that is 1 mm thick, and the walls are built 4 mm high before a flat-bottomed ceiling is built.
The inner regions of the L10 legs are completely sealed once the parts are built so the resulting gas
and powder filled pockets preclude heat treatments until EDM cutting of the parts is completed.

Figure 4: Leg numbering and expanded view of the scan strategy (Layer 50) that constructs the
thin-wall structures within Leg 10 (L10).

## 2.3 Scan strategy (excerpts)

The thin-wall members that lie within Leg 10 of each part have laser scan order and timing shown in
Figure 7. The order and direction each track is scanned in the thin-wall region is the same for every
layer.

The solid part of the bridge structure starts at Layer 175 (height of 7 mm), where the gaps between
legs merge.

The 11 tabs on top of the bridge structure start at Layer 301, as shown in Figure 9. These are
scanned in a similar sequence as the rest of the structure. This results in each pair of tabs to be
scanned together before proceeding to the next region.

## 3.4 Part Distortion (measurement context only)

After being built, the part remains on a section of the build plate. The tops of all 11 ridges are
skim cut parallel to the build plate to remove the rough as-built surface to allow for more accurate
measurement. The vertical height, relative to the surrounding base plate, of every other ridge on the
top surface of the part is measured using a coordinate measurement machine (CMM).

## Process facts relevant to geometry

- Layer thickness 40 µm (Layer 175 begins the solid bridge at 7 mm; Layer 301 begins the tabs at 12 mm).
- Nominal laser spot diameter on the AMMT is on the order of 0.1 mm; the "single laser track" and
  "double laser track" wall widths are not dimensioned in the description. Treat them as open
  questions unless a source gives them.
