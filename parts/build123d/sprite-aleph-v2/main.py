"""Sprite Aleph v2: rigid placements of the supplied, unchanged STEP bodies.

Matrices map input coordinates into assembly millimetres. Result order follows
AssemblyContract.parts; imported internal components are preserved, never fused.
"""

from pathlib import Path

from build123d import Plane, import_step

here = Path(__file__).resolve().parent

body_inputs = {
    "mainFrame": "inputs/sprite-aleph-v2-main-frame.step",
    "rearMount": "inputs/sprite-aleph-v2-rear-mount.step",
    "rearShell": "inputs/sprite-aleph-v2-rear-shell.step",
    "launchPad": "inputs/sprite-aleph-v2-launch-pad.step",
    "ark4in1Esc": "inputs/sprite-aleph-v2-esc-envelope.step",
    "motorCover1": "inputs/sprite-aleph-v2-motor-cover.step",
    "motorCover2": "inputs/sprite-aleph-v2-motor-cover.step",
    "motorCover3": "inputs/sprite-aleph-v2-motor-cover.step",
    "motorCover4": "inputs/sprite-aleph-v2-motor-cover.step",
    "camMountL": "inputs/sprite-aleph-v2-cam-mount-l.step",
    "camMountR": "inputs/sprite-aleph-v2-cam-mount-r.step",
    "rearCoverMount": "inputs/sprite-aleph-v2-rear-cover-mount.step",
    "mountingSled": "inputs/sprite-aleph-v2-sled.step",
    "mainShell": "inputs/sprite-aleph-v2-main-shell.step",
    "topCover": "inputs/sprite-aleph-v2-top-cover.step",
    "servoMount": "inputs/sprite-aleph-v2-servo-mount.step",
    "vtxMount": "inputs/sprite-aleph-v2-vtx-mount.step",
    "alephBase": "inputs/alephBase.step",
    "alephCarrier": "inputs/alephCarrier.step",
    "alephModule": "inputs/alephModule.step",
    "alephHeatsink": "inputs/alephHeatsink.step",
    "alephStandoff1": "inputs/alephStandoff1.step",
    "alephStandoff2": "inputs/alephStandoff2.step",
    "alephStandoff3": "inputs/alephStandoff3.step",
    "alephStandoff4": "inputs/alephStandoff4.step",
    "shellScrew1": "inputs/shellScrew1.step",
    "shellScrew2": "inputs/shellScrew2.step",
    "shellScrew3": "inputs/shellScrew3.step",
    "shellScrew4": "inputs/shellScrew4.step",
    "battery": "inputs/battery.step",
    "regulator": "inputs/regulator.step",
}

placements = {
    "mainFrame": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "rearMount": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "rearShell": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "launchPad": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "ark4in1Esc": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "motorCover1": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "motorCover2": [[0.0, -1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "motorCover3": [[-1.0, 0.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "motorCover4": [[0.0, 1.0, 0.0, 0.0], [-1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "camMountL": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 2.93], [0.0, 0.0, 1.0, -0.54], [0.0, 0.0, 0.0, 1.0]],
    "camMountR": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, -17.28], [0.0, 0.0, 1.0, 19.76], [0.0, 0.0, 0.0, 1.0]],
    "rearCoverMount": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, -11.05], [0.0, 0.0, 0.0, 1.0]],
    "mountingSled": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "mainShell": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "topCover": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "servoMount": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "vtxMount": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "alephBase": [[0.0, 0.0, -1.0, 17.6], [0.0, -1.0, 0.0, 24.75], [-1.0, 0.0, 0.0, 107.0], [0.0, 0.0, 0.0, 1.0]],
    "alephCarrier": [[0.0, 0.0, -1.0, 17.6], [0.0, -1.0, 0.0, 24.75], [-1.0, 0.0, 0.0, 107.0], [0.0, 0.0, 0.0, 1.0]],
    "alephModule": [[0.0, 0.0, -1.0, 17.6], [0.0, -1.0, 0.0, 24.75], [-1.0, 0.0, 0.0, 107.0], [0.0, 0.0, 0.0, 1.0]],
    "alephHeatsink": [[0.0, 0.0, -1.0, 17.6], [0.0, -1.0, 0.0, 24.75], [-1.0, 0.0, 0.0, 107.0], [0.0, 0.0, 0.0, 1.0]],
    "alephStandoff1": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "alephStandoff2": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "alephStandoff3": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "alephStandoff4": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "shellScrew1": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "shellScrew2": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "shellScrew3": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "shellScrew4": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "battery": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "regulator": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
}

result = []
for body_name, relative_path in body_inputs.items():
    matrix = placements[body_name]
    pose = Plane(
        origin=tuple(matrix[i][3] for i in range(3)),
        x_dir=tuple(matrix[i][0] for i in range(3)),
        z_dir=tuple(matrix[i][2] for i in range(3)),
    ).location
    body = import_step(here / relative_path).moved(pose)
    body.label = body_name
    result.append(body)
