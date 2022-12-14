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

import tools.models.data

IU_PER_MM = pcbnew.IU_PER_MILS / 2.54 * 1000
VIEW_BOX_DIVIDER = 100  # Why that value? Wish I knew

# Colors of the SVG generated by kicad, used by .replace to change the pcb colors
KICAD_THEME_SEARCH = tools.models.data.PcbColor(
	key="green_enig",
	name="Green ENIG",
	top_silkscreen="-----unknown-----",
	top_mask="D864FF",
	top_layer="C83434",
	edge_cuts="D0D2CD",
	bottom_layer="C83434",
	bottom_mask="D864FF",
	bottom_silkscreen="-----unknown-----",
	drill="ECECEC",
)

THEMES = [
	tools.models.data.PcbColor(
		key="green_enig",
		name="Green ENIG",
		top_silkscreen="ffffff",
		top_mask="43a047",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="43a047",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="red_enig",
		name="Red ENIG",
		top_silkscreen="ffffff",
		top_mask="ef5350",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="ef5350",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="blue_enig",
		name="Blue ENIG",
		top_silkscreen="ffffff",
		top_mask="1976d2",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="1976d2",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="yellow_enig",
		name="Yellow ENIG",
		top_silkscreen="ffffff",
		top_mask="fbc02d",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="fbc02d",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="purple_enig",
		name="Purple ENIG",
		top_silkscreen="ffffff",
		top_mask="ab47bc",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="ab47bc",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="pink_enig",
		name="Pink ENIG",
		top_silkscreen="ffffff",
		top_mask="f06292",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="f06292",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="transparent_enig",
		name="Transparent ENIG",
		top_silkscreen="ffffff",
		top_mask="8c6104",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="8c6104",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="white_enig",
		name="Yellow ENIG",
		top_silkscreen="000000",
		top_mask="e8e8e8",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="e8e8e8",
		bottom_silkscreen="000000",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="black_enig",
		name="Black ENIG",
		top_silkscreen="ffffff",
		top_mask="252525",
		top_layer="ffb300",
		edge_cuts="D0D2CD",
		bottom_layer="ffb300",
		bottom_mask="252525",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="green_hasl",
		name="Green HASL",
		top_silkscreen="ffffff",
		top_mask="43a047",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="43a047",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="red_hasl",
		name="Red HASL",
		top_silkscreen="ffffff",
		top_mask="ef5350",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="ef5350",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="blue_hasl",
		name="Blue HASL",
		top_silkscreen="ffffff",
		top_mask="1976d2",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="1976d2",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="yellow_hasl",
		name="Yellow HASL",
		top_silkscreen="ffffff",
		top_mask="fbc02d",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="fbc02d",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="purple_hasl",
		name="Purple HASL",
		top_silkscreen="ffffff",
		top_mask="ab47bc",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="ab47bc",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="pink_hasl",
		name="Pink HASL",
		top_silkscreen="ffffff",
		top_mask="f06292",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="f06292",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="transparent_hasl",
		name="Transparent HASL",
		top_silkscreen="ffffff",
		top_mask="8c6104",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="8c6104",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="white_hasl",
		name="Yellow HASL",
		top_silkscreen="000000",
		top_mask="e8e8e8",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="e8e8e8",
		bottom_silkscreen="000000",
		drill="484848",
	),
	tools.models.data.PcbColor(
		key="black_hasl",
		name="Black HASL",
		top_silkscreen="ffffff",
		top_mask="252525",
		top_layer="e6e3e3",
		edge_cuts="D0D2CD",
		bottom_layer="e6e3e3",
		bottom_mask="252525",
		bottom_silkscreen="ffffff",
		drill="484848",
	),
]

THEMES_DICT = {}
for theme in THEMES:
	THEMES_DICT[theme.key] = theme

def generate_svg_from_pcb(filename: str, pcb_theme: typing.Union[None, str] = None) -> tools.models.data.PcbExportedSVGRenders:
	print(filename)
	if pcb_theme in THEMES_DICT:
		pcb_theme = THEMES_DICT[pcb_theme]
	else:
		pcb_theme = THEMES[0]

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

		# If kicad api was properly exposed (missing proxies for PAGE_INFO and multiple other), you could simply do to re-size the svg:
		#   currpageInfo = board.GetPageSettings()
		#   currpageInfo.SetWidthMils(int(pcb_bounding_box.GetWidth() / pcbnew.IU_PER_MILS))
		#   currpageInfo.SetHeightMils(int(pcb_bounding_box.GetHeight() / pcbnew.IU_PER_MILS))
		#   board.SetPageSettings(currpageInfo)
		# Instead we need to hack our way to a proper SVG by modifying the header by hand later with the values from the bounding box

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

		# Mask layer and Copper layer needs to be inverted because the mask isn't a negative mask
		top_layer = top_layer.decode("utf8")\
			.replace(KICAD_THEME_SEARCH.top_silkscreen, pcb_theme.top_silkscreen)\
			.replace(KICAD_THEME_SEARCH.top_mask, pcb_theme.top_layer)\
			.replace(KICAD_THEME_SEARCH.top_layer, pcb_theme.top_mask)\
			.replace(KICAD_THEME_SEARCH.edge_cuts, pcb_theme.edge_cuts)\
			.replace(KICAD_THEME_SEARCH.drill, pcb_theme.drill)
		bottom_layer = bottom_layer.decode("utf8")\
			.replace(KICAD_THEME_SEARCH.bottom_silkscreen, pcb_theme.bottom_silkscreen)\
			.replace(KICAD_THEME_SEARCH.bottom_mask, pcb_theme.bottom_layer)\
			.replace(KICAD_THEME_SEARCH.bottom_layer, pcb_theme.bottom_mask)\
			.replace(KICAD_THEME_SEARCH.edge_cuts, pcb_theme.edge_cuts)\
			.replace(KICAD_THEME_SEARCH.drill, pcb_theme.drill)

	return tools.models.data.PcbExportedSVGRenders(
		top=top_layer,
		bottom=bottom_layer,
	)
