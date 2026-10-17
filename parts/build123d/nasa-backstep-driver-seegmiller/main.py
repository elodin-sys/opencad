from build123d import Align, Box, Pos

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
assert downstreamHeight > stepHeight, "infeasible: downstreamHeight must clear the step"
assert abs(roofAngle) < 90.0, "infeasible: roofAngle must be below vertical"
assert upstreamLength > 0, "infeasible: upstreamLength must be positive"
assert downstreamLength > 0, "infeasible: downstreamLength must be positive"

# [flowDomain] six-edge stepped air solid: envelope minus under-step
domain = Pos(-upstreamLength, 0, 0) * Box(
    upstreamLength + downstreamLength,
    channelWidth,
    downstreamHeight,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
overshoot = 0.05
under_step = Pos(-upstreamLength - overshoot, -overshoot, -overshoot) * Box(
    upstreamLength + overshoot,
    channelWidth + 2 * overshoot,
    stepHeight + overshoot,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
result = domain - under_step
