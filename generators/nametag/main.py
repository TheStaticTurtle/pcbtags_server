import base64
import io
import os
import re
import tempfile
import zipfile
import qrcode
import qrcode.image.svg
from qrcode.util import mode_sizes_for_version
from svgpathtools import Path, Line, CubicBezier
from generators.nametag.exception import NametagGeneratorException, QRCodeNametagGeneratorException
import tools.kicad.defaults
from tools.kicad import pcb2gerber, pcb2svg
from tools.kicad.math import getTextWidth
from tools.kicad.nodes import PcbGraphicsArcNode, PcbViaNode, PcbNetNode, PcbGraphicsSvgNode, PcbGraphicsPolyNode, PcbZoneNode, PcbGraphicsLineNode, PcbGraphicsTextNode
from tools.profiler import Profiler

def remap(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

QRCODE_VERSION_SCALE = {
	1: 5.68,
	2: 4.75,
	3: 4.1,
	4: 3.6,
	5: 3.22,
	6: 2.9,
	7: 2.65,
	8: 2.425,
	9: 2.24,
	10: 2.08,
	11: 1.95,
	# 12: 1.82,
	# 13: 1.71,
}

def generate(canvas: str, color: str, **kwargs):
	profiler = Profiler()
	profiler.start()

	pcb = tools.kicad.defaults.default()
	pcb.add_child(PcbNetNode(0, ""))
	pcb.add_child(PcbNetNode(1, "GND"))

	# Keychain
	start_x = 0  # mm
	tag_half_height = 6.25
	tag_hole_diameter = 4
	copper_fill_half_height = tag_half_height + 2

	x = start_x
	if not kwargs["add_keychain_hole"]:
		x -= tag_hole_diameter * 1.5
		if kwargs["draw_qrcode"]:
			x += 1.5

	if kwargs["draw_qrcode"]:
		vcard  = f"BEGIN:VCARD\n"
		vcard += f"VERSION:3.0\n"
		vcard += f"N:{kwargs['lastname']};{kwargs['firstname']}\n"
		vcard += f"EMAIL:{kwargs['email']}\n"
		vcard += f"TEL;TYPE=CELL:{kwargs['phone']}\n"
		vcard += f"END:VCARD"

		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=1,
			border=0,
		)
		qr.add_data(vcard)
		qr.make(fit=True)

		if qr.version not in QRCODE_VERSION_SCALE:
			raise QRCodeNametagGeneratorException("QR Code is contains too much data to be readable once printed")

		svg_stream = io.BytesIO()
		qr.make_image(fill_color="black", back_color="white", image_factory=qrcode.image.svg.SvgImage).save(svg_stream)
		svg_code = svg_stream.getvalue().decode("utf8").replace("mm", "")

		x += tag_half_height / 1.5
		code = PcbGraphicsSvgNode(io.StringIO(svg_code), x, -tag_half_height+0.3, QRCODE_VERSION_SCALE[qr.version], "F.Mask")
		pcb.add_child(code)

		name_x = code.last_x + tag_half_height / 4 + 0.5
		start_x_after_code = code.last_x + tag_half_height / 4
	else:
		name_x = x + tag_half_height / 1.25 + 0.5
		start_x_after_code = x + tag_half_height / 1.25

	# Lastname
	text_node = PcbGraphicsTextNode(kwargs['lastname'], name_x, -3.125, "F.Mask", (3, 3.4), 0.6)
	text_size = getTextWidth(text_node)
	text_node.x += text_size.w / 2
	name_x += text_size.w
	pcb.add_child(text_node)
	name_x += 2
	# Firstname
	text_node = PcbGraphicsTextNode(kwargs['firstname'], name_x, -3.125, "F.Mask", (3, 3.4), 0.35)
	text_size = getTextWidth(text_node)
	text_node.x += text_size.w / 2
	name_x += text_size.w
	pcb.add_child(text_node)
	name_x += 2

	# Email
	email_x = start_x_after_code + 0.75
	text_node = PcbGraphicsTextNode(kwargs['email'], email_x, 1.7, "F.Mask", (1.7, 1.7), 0.18)
	text_size = getTextWidth(text_node)
	text_node.x += text_size.w / 2
	email_x += text_size.w
	pcb.add_child(text_node)

	# Phone
	phone_x = start_x_after_code + 0.3
	text_node = PcbGraphicsTextNode(kwargs['phone'], phone_x, 4.4, "F.Mask", (1.65, 1.65), 0.18)
	text_size = getTextWidth(text_node)
	text_node.x += text_size.w / 2
	phone_x += text_size.w
	pcb.add_child(text_node)

	# Margins & Separator line
	end = max(name_x, max(phone_x + 1.5, email_x))
	pcb.add_child(PcbGraphicsLineNode(start_x_after_code, 0, end, 0, 0.6, "F.Mask"))

	tag_length = end - tag_half_height / 2
	pcb.add_child(PcbGraphicsLineNode(0, +tag_half_height, tag_length, +tag_half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsLineNode(0, -tag_half_height, tag_length, -tag_half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsArcNode(0, +tag_half_height, -tag_half_height, 0, 0, -tag_half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsArcNode(tag_length, -tag_half_height, tag_length + tag_half_height, 0, tag_length, tag_half_height, 0.254, "Edge.Cuts"))

	if kwargs["add_keychain_hole"]:
		pcb.add_child(PcbViaNode(0, 0, tag_hole_diameter + 0.25, tag_hole_diameter, ["F.Cu", "B.Cu"], 1))

	copper_fill_path = Path()
	copper_fill_path.append(CubicBezier(complex(0, -tag_half_height), complex(-tag_half_height * 1.35, -tag_half_height), complex(-tag_half_height * 1.35, +tag_half_height), complex(0, tag_half_height), ))
	copper_fill_path.append(Line(complex(0, tag_half_height), complex(tag_length, tag_half_height), ))
	copper_fill_path.append(CubicBezier(complex(tag_length, tag_half_height), complex(tag_length + tag_half_height * 1.35, +tag_half_height), complex(tag_length + tag_half_height * 1.35, -tag_half_height), complex(tag_length, -tag_half_height)))
	copper_fill_path.append(Line(complex(tag_length, -tag_half_height), complex(0, -tag_half_height), ))

	copper_fill_polygon = []
	for i in range(250):
		cp = copper_fill_path.point(i / (250 - 1))
		copper_fill_polygon.append((cp.real, cp.imag))

	k = PcbZoneNode(
		[(tag_length + copper_fill_half_height, copper_fill_half_height), (-copper_fill_half_height, copper_fill_half_height), (-copper_fill_half_height, -copper_fill_half_height), (tag_length + copper_fill_half_height, -copper_fill_half_height) ],
		[{"layer": "F.Cu", "points": copper_fill_polygon}, {"layer": "B.Cu", "points": copper_fill_polygon}, ],
		1, "GND",
		"F&B.Cu"
	)
	pcb.add_child(k)
	profiler.log_event_finished("pcb_generation")

	stream = io.StringIO()
	pcb.write(stream)
	kicad_pcb_content = stream.getvalue()
	profiler.log_event_finished("pcb_to_kicad_export")

	with tempfile.NamedTemporaryFile(suffix=".kicad_pcb", delete=False) as kicad_pcb_file:
		kicad_pcb_file.write(kicad_pcb_content.encode("utf-8"))
	profiler.log_event_finished("pcb_to_kicad_export_saved")

	svgs = pcb2svg.generate_svg_from_gerber_and_drill(kicad_pcb_file.name, theme=color)
	profiler.log_event_finished("gerber_to_svg_conversion")

	with tempfile.TemporaryDirectory() as tmp_dir:
		pcb2gerber.generate_gerber_and_drill(kicad_pcb_file.name, tmp_dir)
		profiler.log_event_finished("gerber_generation")

		with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as gerber_archive_file:
			with zipfile.ZipFile(gerber_archive_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
				for root, dirs, files in os.walk(tmp_dir):
					for file in files:
						zipf.write(os.path.join(root, file), file)
		profiler.log_event_finished("gerber_archive")

	base64_gerber_archive = base64.b64encode(open(gerber_archive_file.name, "rb").read()).decode('utf8')
	profiler.log_event_finished("archive_encoding")

	os.unlink(kicad_pcb_file.name)
	os.unlink(gerber_archive_file.name)
	profiler.log_event_finished("file_cleanup")

	return {
		"kicad": {
			".kicad_pcb": kicad_pcb_content
		},
		"gerber": {
			"render": svgs,
			"archive": base64_gerber_archive
		},
		"profiler": profiler.end(),
	}