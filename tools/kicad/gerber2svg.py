import typing

import gerber
from gerber import load_layer, PCB
from gerber.render import RenderSettings
from gerber.render.cairo_backend import GerberCairoContext
import gerber.render.theme
from PIL import ImageColor

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

def generate_svg_from_gerber_and_drill(gerber_dir, theme: typing.Union[None, str] = None):
	if theme in THEMES_DICT:
		theme = THEMES_DICT[theme]
	else:
		theme = THEMES[4]

	pcb_theme = gerber.render.theme.Theme(
		name=theme["name"],
		background=RenderSettings(hex_to_01rgb(theme["board"][0]), alpha=theme["board"][1], invert=True, mirror=False),
		drill=RenderSettings(hex_to_01rgb(theme["drill"][0]), alpha=theme["drill"][1], invert=False, mirror=False),

		top=RenderSettings(hex_to_01rgb(theme["copper"][0]), alpha=theme["copper"][1], invert=False, mirror=False),
		topmask=RenderSettings(hex_to_01rgb(theme["mask"][0]), alpha=theme["mask"][1], invert=True, mirror=False),
		topsilk=RenderSettings(hex_to_01rgb(theme["silk"][0]), alpha=theme["silk"][1], invert=False, mirror=False),

		bottom=RenderSettings(hex_to_01rgb(theme["copper"][0]), alpha=theme["copper"][1], invert=False, mirror=False),
		bottommask=RenderSettings(hex_to_01rgb(theme["mask"][0]), alpha=theme["mask"][1], invert=True, mirror=False),
		bottomsilk=RenderSettings(hex_to_01rgb(theme["silk"][0]), alpha=theme["silk"][1], invert=False, mirror=False),
	)

	pcb = PCB.from_directory(gerber_dir, verbose=True)

	top_ctx = GerberCairoContext()
	top_ctx.render_layers(pcb.top_layers, None, theme=pcb_theme)

	# top_ctx.render_layer(top_layer, settings=RenderSettings(color=theme.COLORS['enig copper'], alpha=1))
	# top_ctx.render_layer(top_mask_layer, settings=RenderSettings(color=theme.COLORS['black soldermask'], alpha=1))
	# top_ctx.render_layer(top_silk_layer, settings=RenderSettings(color=theme.COLORS['white'], alpha=0.85))
	# outline.render_layer(top_ctx)
	# drill.render_layer(top_ctx)

	bottom_ctx = GerberCairoContext()
	bottom_ctx.render_layers(pcb.bottom_layers, None, theme=pcb_theme)
	# bottom_ctx.render_layer(bottom_layer, settings=RenderSettings(color=theme.COLORS['enig copper'], alpha=1))
	# bottom_ctx.render_layer(bottom_mask_layer, settings=RenderSettings(color=theme.COLORS['black soldermask'], alpha=1))
	# bottom_ctx.render_layer(bottom_silk_layer, settings=RenderSettings(color=theme.COLORS['white'], alpha=0.85))
	# outline.render(bottom_ctx)
	# drill.render(bottom_ctx)

	top_ctx.surface.finish()
	top_ctx.surface_buffer.flush()
	top_ctx.surface_buffer.seek(0)
	bottom_ctx.surface.finish()
	bottom_ctx.surface_buffer.flush()
	bottom_ctx.surface_buffer.seek(0)

	return {
		"top": top_ctx.surface_buffer.read(),
		"bottom": bottom_ctx.surface_buffer.read(),
	}
