import sys

from . import PcbGraphicsTextNode
from dataclasses import dataclass

try:
	import tools.kicad.pcbnew_loader
	tools.kicad.pcbnew_loader.add_kicad_to_path()
	import pcbnew
except Exception:
	print("Failed to import kicad tools")
	sys.exit()

@dataclass
class Box:
	x: float
	y: float
	h: float
	w: float

def getTextWidth(node: PcbGraphicsTextNode):
	board = pcbnew.GetBoard()
	text = pcbnew.PCB_TEXT(board)
	text.SetText(node.text)
	text.SetHorizJustify(-1)
	text.SetTextThickness(pcbnew.FromMM(node.thickness))
	text.SetTextSize(pcbnew.wxSize(pcbnew.FromMM(node.size[0]), pcbnew.FromMM(node.size[1])))

	return Box(
		x=pcbnew.ToMM(text.GetBoundingBox().GetX()),
		y=pcbnew.ToMM(text.GetBoundingBox().GetY()),
		h=pcbnew.ToMM(text.GetBoundingBox().GetHeight()),
		w=pcbnew.ToMM(text.GetBoundingBox().GetWidth()),
	)

