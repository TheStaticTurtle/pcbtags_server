import sys

try:
	import tools.kicad.pcbnew_loader
	tools.kicad.pcbnew_loader.add_kicad_to_path()
	import pcbnew
except Exception:
	print("Failed to import kicad tools")
	sys.exit()

METRIC = True
ZERO_FORMAT = pcbnew.GENDRILL_WRITER_BASE.DECIMAL_FORMAT
INTEGER_DIGITS = 3
MANTISSA_DIGITS = 3
MIRROR_Y_AXIS = False
HEADER = True
OFFSET = pcbnew.wxPoint(0,0)
MERGE_PTH_NPTH = True
DRILL_FILE = True
MAP_FILE = False
REPORTER = None

def generate_gerber_and_drill(filename, output_dir):
	print(filename)
	board = pcbnew.LoadBoard(filename)

	plot_controller = pcbnew.PLOT_CONTROLLER(board)
	plot_options = plot_controller.GetPlotOptions()

	plot_options.SetOutputDirectory(output_dir)
	plot_options.SetPlotFrameRef(False)
	plot_options.SetPlotValue(True)
	plot_options.SetPlotReference(True)
	plot_options.SetPlotInvisibleText(True)
	plot_options.SetPlotViaOnMaskLayer(True)
	plot_options.SetExcludeEdgeLayer(False)
	# plot_options.SetPlotPadsOnSilkLayer(PLOT_PADS_ON_SILK_LAYER)
	# plot_options.SetUseAuxOrigin(PLOT_USE_AUX_ORIGIN)
	plot_options.SetMirror(False)
	# plot_options.SetNegative(PLOT_NEGATIVE)
	# plot_options.SetDrillMarksType(PLOT_DRILL_MARKS_TYPE)
	plot_options.SetScale(1)
	plot_options.SetAutoScale(False)
	plot_options.SetMirror(False)
	plot_options.SetUseGerberAttributes(True)
	plot_options.SetExcludeEdgeLayer(True)  # True will include edge in copper
	plot_options.SetUseAuxOrigin(True)
	# plot_options.SetPlotMode(PLOT_MODE)
	# plot_options.SetLineWidth(pcbnew.FromMM(PLOT_LINE_WIDTH))

	# Set Gerber Options
	plot_options.SetUseGerberAttributes(False)  # True will set it to gerber x2, manyboard fab houses dont like this
	plot_options.SetUseGerberProtelExtensions(True)  # Change extension from default .gbr
	plot_options.SetCreateGerberJobFile(True)
	plot_options.SetSubtractMaskFromSilk(False)  # Gerber only
	plot_options.SetIncludeGerberNetlistInfo(True)


	plot_plan = [
		('F_Cu', pcbnew.F_Cu, 'Front Copper'),
		('B_Cu', pcbnew.B_Cu, 'Back Copper'),
		('F_Paste', pcbnew.F_Paste, 'Front Paste'),
		('B_Paste', pcbnew.B_Paste, 'Back Paste'),
		('F_SilkS', pcbnew.F_SilkS, 'Front SilkScreen'),
		('B_SilkS', pcbnew.B_SilkS, 'Back SilkScreen'),
		('F_Mask', pcbnew.F_Mask, 'Front Mask'),
		('B_Mask', pcbnew.B_Mask, 'Back Mask'),
		('Edge_Cuts', pcbnew.Edge_Cuts, 'Edges'),
		# ('Eco1.User', pcbnew.Eco1_User, 'Eco1 User'),
		# ('Eco2.User', pcbnew.Eco2_User, 'Eco1 User'),
	]

	for layer_info in plot_plan:
		plot_controller.SetLayer(layer_info[1])
		plot_controller.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_GERBER, layer_info[2])
		plot_controller.PlotLayer()

	plot_controller.ClosePlot()

	drill_writer = pcbnew.EXCELLON_WRITER(board)

	drill_writer.SetFormat(METRIC, ZERO_FORMAT, INTEGER_DIGITS, MANTISSA_DIGITS)
	drill_writer.SetOptions(MIRROR_Y_AXIS, HEADER, OFFSET, MERGE_PTH_NPTH)
	drill_writer.CreateDrillandMapFilesSet(output_dir, DRILL_FILE, MAP_FILE, REPORTER)


#
# def generate_svg(filename, output_dir):
# 	print(filename)
# 	board = pcbnew.LoadBoard(filename)
#
# 	plot_controller = pcbnew.PLOT_CONTROLLER(board)
# 	plot_options = plot_controller.GetPlotOptions()
#
# 	plot_options.SetOutputDirectory(output_dir)
# 	plot_options.SetPlotFrameRef(False)
# 	plot_options.SetPlotValue(True)
# 	plot_options.SetPlotReference(True)
# 	plot_options.SetPlotInvisibleText(True)
# 	plot_options.SetPlotViaOnMaskLayer(True)
# 	plot_options.SetExcludeEdgeLayer(False)
# 	# plot_options.SetPlotPadsOnSilkLayer(PLOT_PADS_ON_SILK_LAYER)
# 	# plot_options.SetUseAuxOrigin(PLOT_USE_AUX_ORIGIN)
# 	plot_options.SetMirror(False)
# 	# plot_options.SetNegative(PLOT_NEGATIVE)
# 	# plot_options.SetDrillMarksType(PLOT_DRILL_MARKS_TYPE)
# 	plot_options.SetScale(1)
# 	plot_options.SetAutoScale(False)
# 	plot_options.SetMirror(False)
# 	plot_options.SetUseGerberAttributes(True)
# 	plot_options.SetExcludeEdgeLayer(False);
# 	plot_options.SetUseAuxOrigin(True)
# 	# plot_options.SetPlotMode(PLOT_MODE)
# 	# plot_options.SetLineWidth(pcbnew.FromMM(PLOT_LINE_WIDTH))
#
# 	# Set Gerber Options
# 	plot_options.SetUseGerberAttributes(pcbnew.GERBER_USE_GERBER_ATTRIBUTES)
# 	# plot_options.SetUseGerberProtelExtensions(GERBER_USE_GERBER_PROTEL_EXTENSIONS)
# 	plot_options.SetCreateGerberJobFile(pcbnew.GERBER_CREATE_GERBER_JOB_FILE)
# 	# plot_options.SetSubtractMaskFromSilk(GERBER_SUBTRACT_MASK_FROM_SILK)
# 	plot_options.SetIncludeGerberNetlistInfo(pcbnew.GERBER_INCLUDE_GERBER_NETLIST_INFO)
#
# 	plot_plan = [
# 		('F.Cu', pcbnew.F_Cu, 'Front Copper'),
# 		# ('B.Cu', pcbnew.B_Cu, 'Back Copper'),
# 		# ('F.Paste', pcbnew.F_Paste, 'Front Paste'),
# 		# ('B.Paste', pcbnew.B_Paste, 'Back Paste'),
# 		('F.SilkS', pcbnew.F_SilkS, 'Front SilkScreen'),
# 		# ('B.SilkS', pcbnew.B_SilkS, 'Back SilkScreen'),
# 		('F.Mask', pcbnew.F_Mask, 'Front Mask'),
# 		# ('B.Mask', pcbnew.B_Mask, 'Back Mask'),
# 		('Edge.Cuts', pcbnew.Edge_Cuts, 'Edges'),
# 		# ('Eco1.User', pcbnew.Eco1_User, 'Eco1 User'),
# 		# ('Eco2.User', pcbnew.Eco2_User, 'Eco1 User'),
# 	]
#
# 	for layer_info in plot_plan:
# 		plot_controller.SetLayer(layer_info[1])
# 		plot_controller.OpenPlotfile(layer_info[0], pcbnew.PLOT_FORMAT_GERBER, layer_info[2])
# 		plot_controller.PlotLayer()
#
# 	plot_controller.ClosePlot()
#
# 	drill_writer = pcbnew.EXCELLON_WRITER(board)
#
# 	drill_writer.SetFormat(METRIC, ZERO_FORMAT, INTEGER_DIGITS, MANTISSA_DIGITS)
# 	drill_writer.SetOptions(MIRROR_Y_AXIS, HEADER, OFFSET, MERGE_PTH_NPTH)
# 	drill_writer.CreateDrillandMapFilesSet(output_dir, DRILL_FILE, MAP_FILE, REPORTER)