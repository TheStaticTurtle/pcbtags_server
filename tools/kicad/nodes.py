import io
import math
import typing
import uuid

# Base nodes
from svgpathtools import svg2paths


class Node:
	def __init__(self, name):
		self.name = name

	def write(self, stream: io.StringIO, index: int = 0):
		pass
class ValueNode(Node):
	def __init__(self, name, value, add_quotes):
		super().__init__(name)
		self.value = value
		self.add_quotes = add_quotes

	def write(self, stream: io.StringIO, index: int = 0,):
		spacing = "  "*index
		quotes = "\"" if self.add_quotes else ""
		stream.write(f"{spacing}({self.name} {quotes}{self.value}{quotes})\n")
class ListNode(Node):
	def __init__(self, name):
		super().__init__(name)
		self.children = []

	def add_child(self, node: Node):
		self.children.append(node)

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		stream.write(f"{spacing}({self.name}\n")
		for node in self.children:
			node.write(stream, index=index+1)
		stream.write(f"{spacing})\n")

# PCB nodes
class PcbLayerNode(Node):
	def __init__(self, identifier: int, name: str, type: str, alias=None):
		super().__init__(name)
		self.identifier = identifier
		self.name = name
		self.type = type
		self.alias = alias

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		if self.alias is None:
			stream.write(f"{spacing}({self.identifier} \"{self.name}\" {self.type})\n")
		else:
			stream.write(f"{spacing}({self.identifier} \"{self.name}\" {self.type} \"{self.alias}\")\n")
class PcbNetNode(Node):
	def __init__(self, identifier: int, name: str):
		super().__init__(name)
		self.identifier = identifier
		self.name = name

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		stream.write(f"{spacing}(net {self.identifier} \"{self.name}\")\n")
class PcbViaNode(Node):
	def __init__(self, x: float, y: float, size: float, drill: float, layers: typing.List[str], net: int):
		super().__init__("via")
		self.x = x
		self.y = y
		self.size = size
		self.drill = drill
		self.layers = layers
		self.net = net

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		layers = "\"" + ' '.join(self.layers).replace(" ", "\" \"") + "\""
		stream.write(f"{spacing}(via")
		stream.write(f" (at {self.x} {self.y})")
		stream.write(f" (size {self.size})")
		stream.write(f" (drill {self.drill})")
		stream.write(f" (layers {layers})")
		stream.write(f" (net {self.net})")
		stream.write(f" (tstamp {uuid.uuid4()})")
		stream.write(f")\n")
class PcbZoneNode(Node):
	def __init__(self, points: typing.List[typing.Tuple[float, float]], filled_points_groups: typing.List[typing.Dict], net: int, net_name: str, layers: str):
		super().__init__("zone")
		self.points = points
		self.filled_points_groups = filled_points_groups
		self.net = net
		self.net_name = net_name
		self.layers = layers

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		# (zone (net 1) (net_name "GND") (layers F&B.Cu) (tstamp a9bd0d43-e1ef-4c5a-8278-99685938b558) (hatch edge 0.508)
		stream.write(f"{spacing}(zone (net {self.net}) (net_name {self.net_name}) (layers {self.layers}) (tstamp {uuid.uuid4()}) (hatch edge 0.508)")
		stream.write(f"{spacing}  (connect_pads yes (clearance 0))\n")
		stream.write(f"{spacing}  (min_thickness 0.254) (filled_areas_thickness no)\n")
		stream.write(f"{spacing}  (fill yes (thermal_gap 0.508) (thermal_bridge_width 0.508) (smoothing fillet) (island_removal_mode 1) (island_area_min 0))\n")

		stream.write(f"{spacing}  (polygon\n")
		stream.write(f"{spacing}    (pts\n")
		for point in self.points:
			stream.write(f"{spacing}      (xy {point[0]} {point[1]})\n")
		stream.write(f"{spacing}    )\n")
		stream.write(f"{spacing}  )\n")

		for poly in self.filled_points_groups:
			stream.write(f"{spacing}  (filled_polygon\n")
			stream.write(f"{spacing}    (layer \"{poly['layer']}\")\n")
			stream.write(f"{spacing}    (island)\n")
			stream.write(f"{spacing}    (pts\n")
			for point in poly["points"]:
				stream.write(f"{spacing}      (xy {point[0]} {point[1]})\n")
			stream.write(f"{spacing}    )\n")
			stream.write(f"{spacing}  )\n")

		stream.write(f"{spacing})\n")

class PcbGraphicsLineNode(Node):
	def __init__(self, x1: float, y1: float, x2: float, y2: float, width: float, layer: str):
		super().__init__("gr_line")
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.width = width
		self.layer = layer

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		stream.write(f"{spacing}(gr_line (start {self.x1} {self.y1}) (end {self.x2} {self.y2}) (layer \"{self.layer}\") (width {self.width}) (tstamp {uuid.uuid4()}))\n")
class PcbGraphicsRectNode(Node):
	def __init__(self, x_start: float, y_start: float, x_end: float, y_end: float, width: float, layer: str, fill: str = "none"):
		super().__init__("gr_rect")
		self.x_start = x_start
		self.y_start = y_start
		self.x_end = x_end
		self.y_end = y_end
		self.width = width
		self.layer = layer
		self.fill = fill

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		stream.write(f"{spacing}(gr_rect (start {self.x_start} {self.y_start}) (end {self.x_end} {self.y_end}) (layer \"{self.layer}\") (width {self.width}) (fill {self.fill}) (tstamp {uuid.uuid4()}))\n")
class PcbGraphicsPolyNode(Node):
	def __init__(self, points: typing.List[typing.Tuple[float, float]], width: float, layer: str, fill: str = "none"):
		super().__init__("gr_poly")
		self.points = points
		self.width = width
		self.layer = layer
		self.fill = fill

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index

		stream.write(f"{spacing}(gr_poly\n")
		stream.write(f"{spacing}  (pts\n")
		for point in self.points:
			stream.write(f"{spacing}    (xy {point[0]} {point[1]})\n")
		stream.write(f"{spacing}  ) (layer \"{self.layer}\") (width {self.width}) (fill {self.fill}) (tstamp {uuid.uuid4()})\n")
		stream.write(f"{spacing})\n")
class PcbGraphicsTextNode(Node):
	def __init__(self, text: str, x: float, y: float, layer: str, size: tuple, thickness: float):
		super().__init__("gr_line")
		self.text = text
		self.x = x
		self.y = y
		self.size = size
		self.layer = layer
		self.thickness = thickness

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		stream.write(f"{spacing}(gr_text \"{self.text}\" (at {self.x} {self.y}) (layer \"{self.layer}\") (tstamp {uuid.uuid4()})\n")
		stream.write(f"{spacing}  (effects (font (size {self.size[0]} {self.size[1]}) (thickness {self.thickness})))\n")
		stream.write(f"{spacing})\n")
class PcbGraphicsArcNode(Node):
	def __init__(self, x_start: float, y_start: float, x_mid: float, y_mid: float, x_end: float, y_end: float, width: float, layer: str):
		super().__init__("gr_arc")
		self.x_start = x_start
		self.y_start = y_start
		self.x_mid = x_mid
		self.y_mid = y_mid
		self.x_end = x_end
		self.y_end = y_end
		self.width = width
		self.layer = layer

	def write(self, stream: io.StringIO, index: int = 0):
		spacing = "  "*index
		stream.write(f"{spacing}(gr_arc")
		stream.write(f" (start {self.x_start} {self.y_start})")
		stream.write(f" (mid {self.x_mid} {self.y_mid})")
		stream.write(f" (end {self.x_end} {self.y_end})")
		stream.write(f" (layer \"{self.layer}\")")
		stream.write(f" (width {self.width})")
		stream.write(f" (tstamp {uuid.uuid4()})")
		stream.write(f")\n")
class PcbGraphicsSvgNode(Node):
	def __init__(self, svg: typing.Union[str, io.StringIO], x: float, y: float, scale: float, layer: str, precision: int = 18):
		super().__init__("gr_arc")
		self.x = x
		self.y = y
		self.scale = scale
		self.layer = layer

		self.svg_paths, self.svg_attributes = svg2paths(svg) #"C:\\Users\\tugle\\Desktop\\New folder\\test\\spotify_track_4cOdK2wGLETKBW3PvgPWqT.svg")

		self.polygons = []
		self.last_x = -math.inf
		for path in self.svg_paths:
			calculated_precision = precision * len(path._segments)
			polygon_path = []
			for i in range(calculated_precision):
				point = path.point(i / (calculated_precision - 1))
				polygon_path.append((
					float(point.real * self.scale + self.x),
					float(point.imag * self.scale + self.y)
				))
				if polygon_path[-1][0] > self.last_x:
					self.last_x = polygon_path[-1][0]
			self.polygons.append(polygon_path)


	def write(self, stream: io.StringIO, index: int = 0):
		for point_list in self.polygons:
			PcbGraphicsPolyNode(point_list, 0.05, self.layer, fill="solid").write(stream, index)


