import glob
import os
import tempfile
import typing
from PIL import ImageColor
import sys
import xml.etree.ElementTree as xml_et

try:
	import tools.kicad.pcbnew_loader
	tools.kicad.pcbnew_loader.add_kicad_to_path()
	import pcbnew
except Exception:
	print("Failed to import kicad tools")
	sys.exit()


hex_to_01rgb = lambda h: [x / 100 for x in ImageColor.getcolor(h, "RGB")]

THEMES = [
	{
		"key": "black_enig",
		"name": "Black ENIG",
		"board": ["#000000", 1],
		"copper": ["#a15402", 1],
		"mask": ["#000000", 0.85],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "red_enig",
		"name": "Red ENIG",
		"board": ["#300505", 1],
		"copper": ["#a15402", 1],
		"mask": ["#400606", 0.75],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "blue_enig",
		"name": "Red ENIG",
		"board": ["#000000", 1],
		"copper": ["#a15402", 1],
		"mask": ["#04172e", 1],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "yellow_enig",
		"name": "Yellow ENIG",
		"board": ["#6e520d", 1],
		"copper": ["#a15402", 1],
		"mask": ["#6e520d", 1],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "green_enig",
		"name": "Green ENIG",
		"board": ["#1d2200", 1],
		"copper": ["#a15402", 1],
		"mask": ["#00291b", 1],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "white_enig",
		"name": "White ENIG",
		"board": ["#000000", 1],
		"copper": ["#a15402", 1],
		"mask": ["#666666", 0.90],
		"silk": ["#000000", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "purple_enig",
		"name": "Purple ENIG",
		"board": ["#29053b", 1],
		"copper": ["#a15402", 1],
		"mask": ["#29053b", 0.90],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "black_hasl",
		"name": "Black HASL",
		"board": ["#000000", 1],
		"copper": ["#5e5c5c", 1],
		"mask": ["#000000", 0.85],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "red_hasl",
		"name": "Red HASL",
		"board": ["#300505", 1],
		"copper": ["#5e5c5c", 1],
		"mask": ["#400606", 0.75],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "blue_hasl",
		"name": "Blue HASL",
		"board": ["#000000", 1],
		"copper": ["#5e5c5c", 1],
		"mask": ["#04172e", 1],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "yellow_hasl",
		"name": "Yellow HASL",
		"board": ["#6e520d", 1],
		"copper": ["#5e5c5c", 1],
		"mask": ["#6e520d", 1],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "green_hasl",
		"name": "Green HASL",
		"board": ["#1d2200", 1],
		"copper": ["#5e5c5c", 1],
		"mask": ["#00291b", 1],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "white_hasl",
		"name": "White HASL",
		"board": ["#000000", 1],
		"copper": ["#5e5c5c", 1],
		"mask": ["#666666", 0.90],
		"silk": ["#000000", 1],
		"drill": ["#000000", 1],
	}, {
		"key": "purple_hasl",
		"name": "Purple HASL",
		"board": ["#29053b", 1],
		"copper": ["#5e5c5c", 1],
		"mask": ["#29053b", 0.90],
		"silk": ["#ffffff", 1],
		"drill": ["#000000", 1],
	}
]

THEMES_DICT = {}
for theme in THEMES:
	THEMES_DICT[theme["key"]] = theme

IU_PER_MM = pcbnew.IU_PER_MILS / 2.54 * 1000
VIEW_BOX_DIVIDER = 100

def generate_svg_from_gerber_and_drill(filename: str, theme: typing.Union[None, str] = None):
	print(filename)
	if theme in THEMES_DICT:
		theme = THEMES_DICT[theme]
	else:
		theme = THEMES[4]

	board = pcbnew.LoadBoard(filename)

	with tempfile.TemporaryDirectory() as tmp_dir:
		plot_controller = pcbnew.PLOT_CONTROLLER(board)
		plot_options = plot_controller.GetPlotOptions()

		plot_options.SetOutputDirectory(tmp_dir)
		plot_options.SetPlotFrameRef(False)
		plot_options.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.FULL_DRILL_SHAPE)
		plot_options.SetSkipPlotNPTH_Pads(False)
		plot_options.SetMirror(False)
		plot_options.SetFormat(pcbnew.PLOT_FORMAT_SVG)
		plot_options.SetSvgPrecision(4, False)
		plot_options.SetPlotViaOnMaskLayer(True)

		pcb_bounding_box = board.ComputeBoundingBox()

		# If kicad api was properly exposed (missing PAGE_INFO and multiple other), you could simply do to re-size the svg:
		#   currpageInfo = pcb.GetPageSettings()
		#   currpageInfo.SetWidthMils(int(pcb_bounding_box.GetWidth() / pcbnew.IU_PER_MILS))
		#   currpageInfo.SetHeightMils(int(pcb_bounding_box.GetHeight() / pcbnew.IU_PER_MILS))
		#   pcb.SetPageSettings(currpageInfo)
		# Instead we need to modify the SVG header by hand later with the value from the bounding box

		plot_options.SetUseAuxOrigin(True)
		board.GetDesignSettings().SetAuxOrigin(pcb_bounding_box.GetOrigin())

		settings_manager = pcbnew.GetSettingsManager()
		color_settings = settings_manager.GetColorSettings()
		plot_options.SetColorSettings(color_settings)

		new_svg_attributes = {
			"width": f"{round(pcb_bounding_box.GetWidth() / IU_PER_MM, 5)}cm",
			"height": f"{round(pcb_bounding_box.GetHeight() / IU_PER_MM, 5)}cm",
			"viewBox": f"0 0 {int(pcb_bounding_box.GetWidth() / VIEW_BOX_DIVIDER)} {int(pcb_bounding_box.GetHeight() / VIEW_BOX_DIVIDER)}",
		}

		def _export(layers: typing.List, suffix: str, desc: str):
			plot_controller.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_SVG, desc)
			plot_controller.SetColorMode(True)

			for layer in layers:
				plot_controller.SetLayer(layer)
				plot_controller.PlotLayer()

			plot_controller.ClosePlot()

			file = glob.glob1(tmp_dir, f"*-{suffix}.svg")[0]

			tree = xml_et.parse(os.path.join(tmp_dir, file))
			root = tree.getroot()

			for attr, value in new_svg_attributes.items():
				root.attrib[attr] = value

			# tree.write(os.path.join(tmp_dir.name, file))
			print("svg_size_attributes_rewrite")

			return xml_et.tostring(root, encoding='utf8', method='xml')


		top_layer = _export(
			layers=[
				pcbnew.F_Cu,
				pcbnew.F_Mask,
				pcbnew.F_SilkS,
				pcbnew.Edge_Cuts,
			],
			suffix="top_layer",
			desc="Top layer"
		)

		bottom_layer = _export(
			layers=[
				pcbnew.B_Cu,
				pcbnew.B_Mask,
				pcbnew.B_SilkS,
				pcbnew.Edge_Cuts,
			],
			suffix="top_layer",
			desc="Top layer"
		)


	return {
		"top": top_layer,
		"bottom": bottom_layer,
	}
