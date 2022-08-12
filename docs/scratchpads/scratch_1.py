import glob
import pathlib
import xml.etree.ElementTree as xml_et

import tools.kicad.pcbnew_loader
tools.kicad.pcbnew_loader.add_kicad_to_path()
import pcbnew

OUTPUT_DIR = pathlib.Path("C:\\Users\\tugle\\Desktop\\New folder\\test\\New folder")

pcb = pcbnew.LoadBoard("C:\\Users\\tugle\\Desktop\\New folder\\test\\test2.kicad_pcb")

print("board_load")

plot_controller = pcbnew.PLOT_CONTROLLER(pcb)

plot_options = plot_controller.GetPlotOptions()

plot_options.SetOutputDirectory(str(OUTPUT_DIR))
plot_options.SetPlotFrameRef(False)
plot_options.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.FULL_DRILL_SHAPE)
plot_options.SetSkipPlotNPTH_Pads(False)
plot_options.SetMirror(False)
plot_options.SetFormat(pcbnew.PLOT_FORMAT_SVG)
plot_options.SetSvgPrecision(4, False)
plot_options.SetPlotViaOnMaskLayer(True)

pcb_bounding_box = pcb.ComputeBoundingBox()

# If kicad api was properly exposed (missing PAGE_INFO and multiple other), you could simply do:
#   currpageInfo = pcb.GetPageSettings()
#   currpageInfo.SetWidthMils(int(pcb_bounding_box.GetWidth() / pcbnew.IU_PER_MILS))
#   currpageInfo.SetHeightMils(int(pcb_bounding_box.GetHeight() / pcbnew.IU_PER_MILS))
#   pcb.SetPageSettings(currpageInfo)
# Instead we need to modify the SVG header by hand later with the value from the bounding box

plot_options.SetUseAuxOrigin(True)
pcb.GetDesignSettings().SetAuxOrigin(pcb_bounding_box.GetOrigin())

settings_manager = pcbnew.GetSettingsManager()
color_settings = settings_manager.GetColorSettings()
plot_options.SetColorSettings(color_settings)



# plot_options.SetExcludeEdgeLayer(False)
# plot_options.SetMirror(False)
# plot_options.SetExcludeEdgeLayer(True)

# layer_set = pcbnew.LSET()
# layer_set.addLayer(pcbnew.Edge_Cuts)
#
# plot_options.SetLayerSelection(layer_set)

OUTPUT_SUFFIX = "test"
plot_controller.OpenPlotfile("test", pcbnew.PLOT_FORMAT_SVG, "mask")

plot_controller.SetColorMode(True)


plot_controller.SetLayer(pcbnew.F_Cu)
plot_controller.PlotLayer()

# plot_options.SetPlotMode(0)
plot_controller.SetLayer(pcbnew.F_Mask)
plot_controller.PlotLayer()
# plot_options.SetPlotMode(1)

plot_controller.SetLayer(pcbnew.Edge_Cuts)
plot_controller.PlotLayer()

plot_controller.ClosePlot()

print("svg_plot")


IU_PER_MM = pcbnew.IU_PER_MILS / 2.54 * 1000
VIEW_BOX_DIVIDER = 100

new_svg_attributes = {
	"width": f"{round(pcb_bounding_box.GetWidth() / IU_PER_MM, 5)}cm",
	"height": f"{round(pcb_bounding_box.GetHeight() / IU_PER_MM, 5)}cm",
	"viewBox": f"0 0 {int(pcb_bounding_box.GetWidth() / VIEW_BOX_DIVIDER)} {int(pcb_bounding_box.GetHeight() / VIEW_BOX_DIVIDER)}",
}
print(f"Calculated SVG header: {new_svg_attributes}")

file = glob.glob1(str(OUTPUT_DIR), f"*-{OUTPUT_SUFFIX}.svg")[0]

tree = xml_et.parse(OUTPUT_DIR / file)
root = tree.getroot()

for attr, value in new_svg_attributes.items():
	root.attrib[attr] = value

tree.write(OUTPUT_DIR / file)
print("svg_size_attributes_rewrite")


#
# F_Cu = _pcbnew.F_Cu
# In1_Cu = _pcbnew.In1_Cu
# In2_Cu = _pcbnew.In2_Cu
# In3_Cu = _pcbnew.In3_Cu
# In4_Cu = _pcbnew.In4_Cu
# In5_Cu = _pcbnew.In5_Cu
# In6_Cu = _pcbnew.In6_Cu
# In7_Cu = _pcbnew.In7_Cu
# In8_Cu = _pcbnew.In8_Cu
# In9_Cu = _pcbnew.In9_Cu
# In10_Cu = _pcbnew.In10_Cu
# In11_Cu = _pcbnew.In11_Cu
# In12_Cu = _pcbnew.In12_Cu
# In13_Cu = _pcbnew.In13_Cu
# In14_Cu = _pcbnew.In14_Cu
# In15_Cu = _pcbnew.In15_Cu
# In16_Cu = _pcbnew.In16_Cu
# In17_Cu = _pcbnew.In17_Cu
# In18_Cu = _pcbnew.In18_Cu
# In19_Cu = _pcbnew.In19_Cu
# In20_Cu = _pcbnew.In20_Cu
# In21_Cu = _pcbnew.In21_Cu
# In22_Cu = _pcbnew.In22_Cu
# In23_Cu = _pcbnew.In23_Cu
# In24_Cu = _pcbnew.In24_Cu
# In25_Cu = _pcbnew.In25_Cu
# In26_Cu = _pcbnew.In26_Cu
# In27_Cu = _pcbnew.In27_Cu
# In28_Cu = _pcbnew.In28_Cu
# In29_Cu = _pcbnew.In29_Cu
# In30_Cu = _pcbnew.In30_Cu
# B_Cu = _pcbnew.B_Cu
# B_Adhes = _pcbnew.B_Adhes
# F_Adhes = _pcbnew.F_Adhes
# B_Paste = _pcbnew.B_Paste
# F_Paste = _pcbnew.F_Paste
# B_SilkS = _pcbnew.B_SilkS
# F_SilkS = _pcbnew.F_SilkS
# B_Mask = _pcbnew.B_Mask
# F_Mask = _pcbnew.F_Mask
# Dwgs_User = _pcbnew.Dwgs_User
# Cmts_User = _pcbnew.Cmts_User
# Eco1_User = _pcbnew.Eco1_User
# Eco2_User = _pcbnew.Eco2_User
# Edge_Cuts = _pcbnew.Edge_Cuts
# Margin = _pcbnew.Margin
# B_CrtYd = _pcbnew.B_CrtYd
# F_CrtYd = _pcbnew.F_CrtYd
# B_Fab = _pcbnew.B_Fab
# F_Fab = _pcbnew.F_Fab
# User_1 = _pcbnew.User_1
# User_2 = _pcbnew.User_2
# User_3 = _pcbnew.User_3
# User_4 = _pcbnew.User_4
# User_5 = _pcbnew.User_5
# User_6 = _pcbnew.User_6
# User_7 = _pcbnew.User_7
# User_8 = _pcbnew.User_8
# User_9 = _pcbnew.User_9