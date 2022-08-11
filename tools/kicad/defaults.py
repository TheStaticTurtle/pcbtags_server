from tools.kicad import ListNode, ValueNode, PcbLayerNode


def default_document() -> ListNode:
	doc = ListNode("kicad_pcb")
	doc.add_child(ValueNode("version", "20211014", False))
	doc.add_child(ValueNode("generator", "pcbnew", True))

	general = ListNode("general")
	general.add_child(ValueNode("thickness", "1.6", False))
	doc.add_child(general)

	doc.add_child(ValueNode("paper", "A4", True))

	return doc


def default_layers() -> ListNode:
	layers = ListNode("layers")
	layers.add_child(PcbLayerNode(0, "F.Cu", "signal"))
	layers.add_child(PcbLayerNode(31, "B.Cu", "signal"))
	layers.add_child(PcbLayerNode(32, "B.Adhes", "user", "B.Adhesive"))
	layers.add_child(PcbLayerNode(33, "F.Adhes", "user", "F.Adhesive"))
	layers.add_child(PcbLayerNode(34, "B.Paste", "user"))
	layers.add_child(PcbLayerNode(35, "F.Paste", "user"))
	layers.add_child(PcbLayerNode(36, "B.SilkS", "user", "B.Silkscreen"))
	layers.add_child(PcbLayerNode(37, "F.SilkS", "user", "F.Silkscreen"))
	layers.add_child(PcbLayerNode(38, "B.Mask", "user"))
	layers.add_child(PcbLayerNode(39, "F.Mask", "user"))
	layers.add_child(PcbLayerNode(40, "Dwgs.User", "user", "User.Drawings"))
	layers.add_child(PcbLayerNode(41, "Cmts.User", "user", "User.Comments"))
	layers.add_child(PcbLayerNode(42, "Eco1.User", "user", "User.Eco1"))
	layers.add_child(PcbLayerNode(43, "Eco2.User", "user", "User.Eco2"))
	layers.add_child(PcbLayerNode(44, "Edge.Cuts", "user"))
	layers.add_child(PcbLayerNode(45, "Margin", "user"))
	layers.add_child(PcbLayerNode(46, "B.CrtYd", "user", "B.Courtyard"))
	layers.add_child(PcbLayerNode(47, "F.CrtYd", "user", "F.Courtyard"))
	layers.add_child(PcbLayerNode(48, "B.Fab", "user"))
	layers.add_child(PcbLayerNode(49, "F.Fab", "user"))
	layers.add_child(PcbLayerNode(50, "User.1", "user"))
	layers.add_child(PcbLayerNode(51, "User.2", "user"))
	layers.add_child(PcbLayerNode(52, "User.3", "user"))
	layers.add_child(PcbLayerNode(53, "User.4", "user"))
	layers.add_child(PcbLayerNode(54, "User.5", "user"))
	layers.add_child(PcbLayerNode(55, "User.6", "user"))
	layers.add_child(PcbLayerNode(56, "User.7", "user"))
	layers.add_child(PcbLayerNode(57, "User.8", "user"))
	layers.add_child(PcbLayerNode(58, "User.9", "user"))
	return layers

def default_setup() -> ListNode:
	setup = ListNode("setup")
	setup.add_child(ValueNode("pad_to_mask_clearance", "0", False))

	setup_pcbplotparams = ListNode("pcbplotparams")
	setup_pcbplotparams.add_child(ValueNode("layerselection", "0x00010fc_ffffffff", False))
	setup_pcbplotparams.add_child(ValueNode("disableapertmacros", "false", False))
	setup_pcbplotparams.add_child(ValueNode("usegerberextensions", "false", False))
	setup_pcbplotparams.add_child(ValueNode("usegerberattributes", "true", False))
	setup_pcbplotparams.add_child(ValueNode("usegerberadvancedattributes", "true", False))
	setup_pcbplotparams.add_child(ValueNode("creategerberjobfile", "true", False))
	setup_pcbplotparams.add_child(ValueNode("svguseinch", "false", False))
	setup_pcbplotparams.add_child(ValueNode("svgprecision", "6", False))
	setup_pcbplotparams.add_child(ValueNode("excludeedgelayer", "true", False))
	setup_pcbplotparams.add_child(ValueNode("plotframeref", "false", False))
	setup_pcbplotparams.add_child(ValueNode("viasonmask", "false", False))
	setup_pcbplotparams.add_child(ValueNode("mode", "1", False))
	setup_pcbplotparams.add_child(ValueNode("useauxorigin", "false", False))
	setup_pcbplotparams.add_child(ValueNode("hpglpennumber", "1", False))
	setup_pcbplotparams.add_child(ValueNode("hpglpenspeed", "20", False))
	setup_pcbplotparams.add_child(ValueNode("hpglpendiameter", "15.000000", False))
	setup_pcbplotparams.add_child(ValueNode("dxfpolygonmode", "true", False))
	setup_pcbplotparams.add_child(ValueNode("dxfimperialunits", "true", False))
	setup_pcbplotparams.add_child(ValueNode("dxfusepcbnewfont", "true", False))
	setup_pcbplotparams.add_child(ValueNode("psnegative", "false", False))
	setup_pcbplotparams.add_child(ValueNode("psa4output", "false", False))
	setup_pcbplotparams.add_child(ValueNode("plotreference", "true", False))
	setup_pcbplotparams.add_child(ValueNode("plotvalue", "true", False))
	setup_pcbplotparams.add_child(ValueNode("plotinvisibletext", "false", False))
	setup_pcbplotparams.add_child(ValueNode("sketchpadsonfab", "false", False))
	setup_pcbplotparams.add_child(ValueNode("subtractmaskfromsilk", "false", False))
	setup_pcbplotparams.add_child(ValueNode("outputformat", "1", False))
	setup_pcbplotparams.add_child(ValueNode("mirror", "false", False))
	setup_pcbplotparams.add_child(ValueNode("drillshape", "1", False))
	setup_pcbplotparams.add_child(ValueNode("scaleselection", "1", False))
	setup_pcbplotparams.add_child(ValueNode("outputdirectory", "", True))
	setup.add_child(setup_pcbplotparams)

	return setup


def default() -> ListNode:
	doc = default_document()
	doc.add_child(default_layers())
	doc.add_child(default_setup())
	return doc