import io
import re
import requests

import tools.kicad.defaults
from tools.kicad.export import kicad_export
from tools.kicad.nodes import PcbGraphicsSvgNode, PcbGraphicsPolyNode
from tools.profiler import Profiler

from .data import SPOTIFY_LOGO_POINTS
from ..common import keychain_base_pcb
from .exception import InvalidURISpotifyGeneratorException, ScannablesCDNSpotifyGeneratorException

OPEN_SPOTIFY_REGEX = re.compile(r"https:\/\/open.spotify.com\/((?:track)|(?:user)|(?:album)|(?:playlist)|(?:artist))\/(.+?)(?:\?|$)")

def is_spotify_uri_valid(uri):
	valid = False
	valid = valid or uri.startswith("spotify:track:")
	valid = valid or uri.startswith("spotify:user:")
	valid = valid or uri.startswith("spotify:playlist:")
	valid = valid or uri.startswith("spotify:album:")
	valid = valid or uri.startswith("spotify:artist:")
	return valid

def generate(canvas: str, color: str, profiler: Profiler, **kwargs):
	pcb = tools.kicad.defaults.make_pcb()
	profiler.log_event("pcbfile_base", facility="generate")

	uri = kwargs["code"]
	if re.match(OPEN_SPOTIFY_REGEX, kwargs["code"]):
		result = OPEN_SPOTIFY_REGEX.search(kwargs["code"])
		print(f"Changing code to: spotify:{result.group(1)}:{result.group(2)}")
		uri = f"spotify:{result.group(1)}:{result.group(2)}"

	if not is_spotify_uri_valid(uri):
		raise InvalidURISpotifyGeneratorException(f"The specified URI ({uri}) is invalid")

	URL = f"https://scannables.scdn.co/uri/plain/svg/ffffff/black/1024/{uri}"
	response = requests.get(URL)
	if response.status_code >= 400:
		raise ScannablesCDNSpotifyGeneratorException(f"Error while retrieving the code from scannables.scdn.com (used: {uri}, response code: {response.status_code})")

	profiler.log_event("scannables_cdn_download", facility="generate")

	svg_without_rect = re.sub(r'<rect .+fill="#ffffff".+>\n', "", response.text)
	svg_only_code = re.sub(r'<g .+g>\n', "", svg_without_rect)

	profiler.log_event("code_processing", facility="generate")

	# Keychain
	tag_half_height = 6.25
	tag_hole_diameter = 4

	logo_x_offset = 0  # mm
	code_start_x = 1  # mm
	if not kwargs["draw_spotify_logo"]:
		code_start_x = -10  # mm
	if not kwargs["add_keychain_hole"]:
		code_start_x -= tag_hole_diameter * 2
		logo_x_offset -= tag_hole_diameter * 2

	code = PcbGraphicsSvgNode(io.StringIO(svg_only_code), code_start_x, -7.5, 0.15, "F.Mask")
	pcb.add_child(code)

	profiler.log_event("code_drawing", facility="generate")

	if kwargs["draw_spotify_logo"]:
		points = [
			(x + logo_x_offset, y)
			for x, y in SPOTIFY_LOGO_POINTS
		]
		logo = PcbGraphicsPolyNode(points, 0.048, "F.Mask", fill="solid")
		pcb.add_child(logo)

		profiler.log_event("logo_drawing", facility="generate")

	tag_length = code.last_x - tag_half_height / 2
	keychain_base_pcb(
		pcb=pcb,
		half_height=tag_half_height,
		length=tag_length,
		hole=kwargs["add_keychain_hole"],
		hole_diameter=tag_hole_diameter
	)

	profiler.log_event("pcb_outline_drawn", facility="generate")

	return kicad_export(pcb, color, profiler=profiler)
