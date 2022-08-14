from svgpathtools import CubicBezier, Line, Path

from tools.kicad.nodes import *

def remap(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def keychain_base_pcb(pcb: ListNode, half_height: float, length: float, hole: bool = True, hole_diameter: float = 4):
	copper_fill_half_height = half_height + 2

	pcb.add_child(PcbGraphicsLineNode(0, +half_height, length, +half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsLineNode(0, -half_height, length, -half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsArcNode(0, +half_height, -half_height, 0, 0, -half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsArcNode(length, -half_height, length + half_height, 0, length, half_height, 0.254, "Edge.Cuts"))
	
	if hole:
		pcb.add_child(PcbViaNode(0, 0, hole_diameter + 0.25, hole_diameter, ["F.Cu", "B.Cu"], 1))

	copper_fill_path = Path()
	copper_fill_path.append(CubicBezier(complex(0, -half_height), complex(-half_height * 1.35, -half_height), complex(-half_height * 1.35, +half_height), complex(0, half_height), ))
	copper_fill_path.append(Line(complex(0, half_height), complex(length, half_height), ))
	copper_fill_path.append(CubicBezier(complex(length, half_height), complex(length + half_height * 1.35, +half_height), complex(length + half_height * 1.35, -half_height), complex(length, -half_height)))
	copper_fill_path.append(Line(complex(length, -half_height), complex(0, -half_height), ))

	copper_fill_polygon = []
	for i in range(250):
		cp = copper_fill_path.point(i / (250 - 1))
		copper_fill_polygon.append((cp.real, cp.imag))

	k = PcbZoneNode(
		[(length + copper_fill_half_height, copper_fill_half_height), (-copper_fill_half_height, copper_fill_half_height), (-copper_fill_half_height, -copper_fill_half_height), (length + copper_fill_half_height, -copper_fill_half_height) ],
		[{"layer": "F.Cu", "points": copper_fill_polygon}, {"layer": "B.Cu", "points": copper_fill_polygon}, ],
		1, "GND",
		"F&B.Cu"
	)
	pcb.add_child(k)
