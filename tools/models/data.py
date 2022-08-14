import typing
from pydantic import BaseModel

class ErrorModel(BaseModel):
	short_text: str
	traceback: str

class GeneratorCanvasSize(BaseModel):
	height: typing.Union[float, None]
	width: typing.Union[float, None]
class GeneratorCanvas(BaseModel):
	text: str
	key: str
	size_min: GeneratorCanvasSize
	size_max: GeneratorCanvasSize
	help: str
class GeneratorOption(BaseModel):
	type: str
	key: str
	text: str
	default: typing.Any
	help: str
class GeneratorInfo(BaseModel):
	caching_allowed: bool
	name: str
	key: str
	desc: str
	short_desc: str
	available_canvases: typing.List[GeneratorCanvas]
	options:  typing.List[GeneratorOption]

class PcbColor(BaseModel):
	key: str
	name: str
	top_silkscreen: str
	top_mask: str
	top_layer: str
	edge_cuts: str
	bottom_layer: str
	bottom_mask: str
	bottom_silkscreen: str
	drill: str

class PcbExportedKicadFiles(BaseModel):
	kicad_pcb: str
class PcbExportedSVGRenders(BaseModel):
	top: str
	bottom: str
class PcbExportedGerber(BaseModel):
	render: PcbExportedSVGRenders
	archive: str
class PcbExportedData(BaseModel):
	kicad: PcbExportedKicadFiles
	gerber: PcbExportedGerber
	profiler: dict