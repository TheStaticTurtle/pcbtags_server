import base64
import os
import tempfile
import zipfile
from dataclasses import dataclass
from svgpathtools import CubicBezier, Line, Path

from tools.kicad import pcb2gerber, pcb2svg
from tools.kicad.nodes import *
from tools.profiler import Profiler


def kicad_export(pcb: ListNode, pcb_theme, profiler: Profiler = None) -> dict:
	if profiler is None:
		profiler = Profiler()

	stream = io.StringIO()
	pcb.write(stream)
	kicad_pcb_content = stream.getvalue()
	profiler.log_event_finished("pcb_to_kicad_export")

	with tempfile.NamedTemporaryFile(suffix=".kicad_pcb", delete=False) as kicad_pcb_file:
		kicad_pcb_file.write(kicad_pcb_content.encode("utf-8"))
	profiler.log_event_finished("pcb_to_kicad_export_saved")

	svgs = pcb2svg.generate_svg_from_gerber_and_drill(kicad_pcb_file.name, theme=pcb_theme)
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