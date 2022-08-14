import io
import qrcode
import qrcode.image.svg

import tools.kicad.defaults
from tools.kicad.export import kicad_export
from tools.kicad.math import getTextWidth
from tools.kicad.nodes import PcbGraphicsSvgNode, PcbGraphicsLineNode, PcbGraphicsTextNode
from tools.profiler import Profiler

from ..common import keychain_base_pcb
from .exception import *

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
	# 12: 1.82,  # Disabled on purpose, too small for the pcb
	# 13: 1.71,
}

def generate(canvas: str, color: str, profiler: Profiler, **kwargs):
	pcb = tools.kicad.defaults.make_pcb()

	# Keychain
	start_x = 0  # mm
	tag_half_height = 6.25
	tag_hole_diameter = 4

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
	keychain_base_pcb(
		pcb=pcb,
		half_height=tag_half_height,
		length=tag_length,
		hole=kwargs["add_keychain_hole"],
		hole_diameter=tag_hole_diameter
	)

	profiler.log_event_finished("pcb_generation")

	return kicad_export(pcb, color, profiler=profiler)