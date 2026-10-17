import cadquery as cq

stepHeight = 12.7
channelWidth = 152.4
downstreamHeight = 114.3
upstreamHeight = 101.6
roofAngle = 0.0
upstreamLength = 1333.5
downstreamLength = 635.0

assert stepHeight > 0, "infeasible: stepHeight must be positive"
assert channelWidth > 0, "infeasible: channelWidth must be positive"
assert downstreamHeight > 0, "infeasible: downstreamHeight must be positive"
assert upstreamHeight > 0, "infeasible: upstreamHeight must be positive"
assert abs(roofAngle) <= 0.001, "infeasible: this model is the parallel-roof case"
assert upstreamLength > 0, "infeasible: upstreamLength must be positive"
assert downstreamLength > 0, "infeasible: downstreamLength must be positive"
assert stepHeight < downstreamHeight, "infeasible: stepHeight exceeds the downstream passage"

# XZ extrudes along -Y; negative distance places the span at y = 0 .. channelWidth.
outline = [
    (-upstreamLength, downstreamHeight),
    (downstreamLength, downstreamHeight),
    (downstreamLength, 0.0),
    (0.0, 0.0),
    (0.0, stepHeight),
    (-upstreamLength, stepHeight),
]
result = cq.Workplane("XZ").polyline(outline).close().extrude(-channelWidth)
