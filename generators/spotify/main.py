import base64
import glob
import io
import os
import re
import sys
import tempfile
import time
import zipfile

import requests
from svgpathtools import Path, Line, CubicBezier
from generators.spotify.exception import InvalidURISpotifyGeneratorException
import tools.kicad.defaults
from tools.kicad import PcbGraphicsLineNode, pcb2gerber, gerber2svg, pcb2svg
from tools.kicad.nodes import PcbGraphicsArcNode, PcbViaNode, PcbNetNode, PcbGraphicsSvgNode, PcbGraphicsPolyNode, PcbZoneNode
from tools.profiler import Profiler

SPOTIFY_LOGO_POINTS = [(9.074399, -4.917528), (9.435994, -4.876703), (9.790608, -4.809652), (10.137025, -4.717188),
                       (10.474032, -4.600122), (10.800413, -4.459265), (11.114955, -4.29543), (11.416442, -4.109428),
                       (11.70366, -3.902071), (11.975393, -3.674169), (12.230428, -3.426535), (12.46755, -3.159981),
                       (12.685544, -2.875317), (12.883196, -2.573356), (13.05929, -2.254909), (13.212613, -1.920788),
                       (13.340457, -1.576113), (13.441116, -1.22642), (13.514874, -0.87314), (13.562016, -0.517708),
                       (13.582828, -0.161555), (13.577595, 0.193886), (13.546601, 0.547182), (13.490131, 0.896899),
                       (13.408471, 1.241606), (13.301905, 1.579869), (13.170719, 1.910256), (13.015198, 2.231334),
                       (12.835626, 2.54167), (12.632288, 2.839832), (12.405469, 3.124386), (12.155456, 3.393901),
                       (11.885941, 3.643914), (11.601387, 3.870733), (11.303225, 4.074071), (10.992889, 4.253643),
                       (10.671811, 4.409164), (10.341424, 4.54035), (10.003161, 4.646916), (9.658454, 4.728576),
                       (9.308737, 4.785046), (8.955441, 4.81604), (8.6, 4.821273), (8.243847, 4.800461),
                       (7.888415, 4.753319), (7.535135, 4.679561), (7.185442, 4.578902), (6.840767, 4.451058),
                       (6.671798, 4.377319), (6.506646, 4.297736), (6.345412, 4.212459), (6.188199, 4.121641),
                       (6.035107, 4.025434), (5.886238, 3.92399), (5.741693, 3.817459), (5.601574, 3.705996),
                       (5.465982, 3.58975), (5.33502, 3.468874), (5.208787, 3.343519), (5.087386, 3.213839),
                       (4.970918, 3.079983), (4.859484, 2.942105), (4.753187, 2.800356), (4.652127, 2.654888),
                       (4.556406, 2.505852), (4.466125, 2.353401), (4.381386, 2.197686), (4.30229, 2.038859),
                       (4.228938, 1.877073), (4.161433, 1.712478), (4.099876, 1.545227), (4.059602, 1.422062),
                       (5.867092, 1.422062), (5.867204, 1.435199), (5.867904, 1.448396), (5.8692, 1.461635),
                       (5.871101, 1.474901), (5.873617, 1.488176), (5.87604, 1.501499), (5.879046, 1.514583),
                       (5.882621, 1.527416), (5.886749, 1.539985), (5.891416, 1.552277), (5.896607, 1.56428),
                       (5.902306, 1.575981), (5.908499, 1.587367), (5.915171, 1.598427), (5.922306, 1.609147),
                       (5.929889, 1.619515), (5.937907, 1.629519), (5.946343, 1.639145), (5.955182, 1.648382),
                       (5.96441, 1.657216), (5.974012, 1.665635), (5.983973, 1.673626), (5.994277, 1.681178),
                       (6.00491, 1.688277), (6.015856, 1.69491), (6.027102, 1.701066), (6.038631, 1.706731),
                       (6.050428, 1.711893), (6.06248, 1.71654), (6.07477, 1.720658), (6.087283, 1.724236),
                       (6.100006, 1.72726), (6.112922, 1.729719), (6.126017, 1.731599), (6.139276, 1.732888),
                       (6.152684, 1.733573), (6.166225, 1.733642), (6.184296, 1.732832), (6.202332, 1.731554),
                       (6.220322, 1.72981), (6.238257, 1.727601), (6.25613, 1.724928), (6.27393, 1.721792),
                       (6.291649, 1.718194), (6.309278, 1.714136), (6.483188, 1.677025), (6.65782, 1.643824),
                       (6.833106, 1.61454), (7.008981, 1.589182), (7.185379, 1.56776), (7.362233, 1.550282),
                       (7.539478, 1.536756), (7.717046, 1.527192), (7.85463, 1.52319), (7.992211, 1.522487),
                       (8.12973, 1.525078), (8.267128, 1.53096), (8.404346, 1.540131), (8.541324, 1.552586),
                       (8.678004, 1.568323), (8.814325, 1.587338), (8.924329, 1.604805), (9.033765, 1.624909),
                       (9.142588, 1.647633), (9.25075, 1.672962), (9.358208, 1.70088), (9.464914, 1.731369),
                       (9.570823, 1.764415), (9.675889, 1.8), (9.780067, 1.838109), (9.883309, 1.878726),
                       (9.985571, 1.921834), (10.086806, 1.967417), (10.18697, 2.01546), (10.286014, 2.065945),
                       (10.383895, 2.118857), (10.480566, 2.17418), (10.490434, 2.180193), (10.500389, 2.186058),
                       (10.510429, 2.191773), (10.520553, 2.197337), (10.530758, 2.20275), (10.541043, 2.208011),
                       (10.551407, 2.213118), (10.561847, 2.218071), (10.574901, 2.223454), (10.588074, 2.228184),
                       (10.601347, 2.232268), (10.614698, 2.235712), (10.62811, 2.238522), (10.641561, 2.240704),
                       (10.655033, 2.242266), (10.668505, 2.243213), (10.681958, 2.24355), (10.695372, 2.243286),
                       (10.722004, 2.240975), (10.748243, 2.236331), (10.77393, 2.229402), (10.798908, 2.220239),
                       (10.823018, 2.208894), (10.846103, 2.195415), (10.857211, 2.187891), (10.868004, 2.179852),
                       (10.878461, 2.171306), (10.888564, 2.162257), (10.898291, 2.152713), (10.907623, 2.14268),
                       (10.916541, 2.132163), (10.925025, 2.12117), (10.933055, 2.109706), (10.940611, 2.097777),
                       (10.938986, 2.091275), (10.946095, 2.078806), (10.95255, 2.066132), (10.958355, 2.053275),
                       (10.963515, 2.040255), (10.968033, 2.027094), (10.971914, 2.013813), (10.975161, 2.000434),
                       (10.977779, 1.986978), (10.979773, 1.973466), (10.981145, 1.959919), (10.9819, 1.946359),
                       (10.982043, 1.932807), (10.981578, 1.919285), (10.980508, 1.905813), (10.97657, 1.879106),
                       (10.970265, 1.852857), (10.966235, 1.839958), (10.961624, 1.827237), (10.956438, 1.814715),
                       (10.950681, 1.802415), (10.944357, 1.790357), (10.937469, 1.778563), (10.930022, 1.767053),
                       (10.922019, 1.75585), (10.913467, 1.744974), (10.904367, 1.734447), (10.894724, 1.724291),
                       (10.884544, 1.714525), (10.873828, 1.705172), (10.862583, 1.696254), (10.853149, 1.68947),
                       (10.843621, 1.682822), (10.834001, 1.676312), (10.824289, 1.669941), (10.814486, 1.663709),
                       (10.804596, 1.657618), (10.794618, 1.651667), (10.784554, 1.645859), (10.66964, 1.57947),
                       (10.553061, 1.516199), (10.434881, 1.456075), (10.315163, 1.399128), (10.193972, 1.345387),
                       (10.071371, 1.294882), (9.947426, 1.247642), (9.8222, 1.203696), (9.593472, 1.133807),
                       (9.362424, 1.073115), (9.129336, 1.021665), (8.894484, 0.9795), (8.658147, 0.946666),
                       (8.420604, 0.923206), (8.182131, 0.909165), (7.943007, 0.904587), (7.617886, 0.920842),
                       (7.455173, 0.930189), (7.292766, 0.941975), (7.147649, 0.956102), (7.002827, 0.972705),
                       (6.85833, 0.99178), (6.71419, 1.01332), (6.57044, 1.037322), (6.427111, 1.063779),
                       (6.284235, 1.092687), (6.141843, 1.124041), (6.130649, 1.126504), (6.119511, 1.129194),
                       (6.108433, 1.13211), (6.097418, 1.135252), (6.08647, 1.138618), (6.075591, 1.142207),
                       (6.064787, 1.146018), (6.054059, 1.150051), (6.04163, 1.155351), (6.029551, 1.161157),
                       (6.017831, 1.16745), (6.006479, 1.174215), (5.995503, 1.181435), (5.984913, 1.189094),
                       (5.974716, 1.197175), (5.964922, 1.205662), (5.95554, 1.214538), (5.946579, 1.223787),
                       (5.938046, 1.233392), (5.929952, 1.243337), (5.922305, 1.253605), (5.915113, 1.26418),
                       (5.908386, 1.275045), (5.902132, 1.286184), (5.89636, 1.29758), (5.891079, 1.309217),
                       (5.886298, 1.321078), (5.882025, 1.333147), (5.878269, 1.345407), (5.87504, 1.357842),
                       (5.872345, 1.370435), (5.870194, 1.383171), (5.868596, 1.396031), (5.867559, 1.409),
                       (5.867092, 1.422062), (4.059602, 1.422062), (4.044367, 1.375471), (3.995009, 1.203363),
                       (3.951903, 1.029054), (3.91515, 0.852696), (3.884852, 0.67444), (3.861111, 0.49444),
                       (3.844027, 0.312845), (3.833702, 0.129809), (3.830238, -0.054516), (3.830238, -0.054517),
                       (5.66554, -0.054517), (5.665991, -0.025412), (5.668642, 0.003264), (5.673426, 0.031411),
                       (5.680277, 0.058928), (5.689129, 0.085712), (5.699915, 0.111664), (5.71257, 0.136681),
                       (5.727028, 0.160663), (5.743221, 0.183509), (5.761085, 0.205117), (5.780552, 0.225387),
                       (5.801557, 0.244216), (5.824033, 0.261505), (5.847914, 0.277152), (5.873134, 0.291056),
                       (5.899627, 0.303115), (5.916172, 0.308655), (5.932886, 0.313457), (5.949744, 0.31752),
                       (5.966723, 0.320844), (5.983799, 0.32343), (6.000947, 0.325277), (6.018143, 0.326385),
                       (6.035364, 0.326754), (6.052584, 0.326385), (6.069781, 0.325277), (6.086929, 0.32343),
                       (6.104005, 0.320844), (6.120984, 0.31752), (6.137843, 0.313457), (6.154557, 0.308655),
                       (6.171102, 0.303115), (6.377626, 0.247271), (6.585808, 0.19885), (6.795446, 0.15788),
                       (7.006341, 0.124389), (7.218291, 0.098405), (7.431097, 0.079957), (7.644558, 0.069072),
                       (7.858474, 0.065778), (8.020196, 0.067774), (8.181765, 0.073507), (8.343114, 0.082973),
                       (8.504181, 0.096164), (8.664899, 0.113076), (8.825205, 0.133702), (8.985033, 0.158035),
                       (9.144319, 0.18607), (9.346421, 0.226104), (9.546772, 0.273286), (9.745185, 0.327553),
                       (9.941473, 0.388845), (10.13545, 0.457098), (10.326929, 0.532252), (10.515723, 0.614244),
                       (10.701647, 0.703012), (10.741738, 0.724024), (10.781581, 0.745532), (10.860753, 0.789575),
                       (11.018641, 0.878577), (11.035355, 0.888285), (11.052357, 0.897051), (11.069614, 0.90488),
                       (11.087094, 0.911781), (11.104766, 0.917761), (11.122597, 0.922828), (11.140555, 0.926989),
                       (11.158608, 0.930251), (11.176725, 0.932623), (11.194872, 0.93411), (11.213019, 0.934721),
                       (11.231133, 0.934463), (11.249182, 0.933344), (11.267135, 0.931371), (11.284958, 0.928551),
                       (11.30262, 0.924892), (11.32009, 0.920401), (11.337334, 0.915086), (11.354322, 0.908954),
                       (11.37102, 0.902013), (11.387398, 0.894269), (11.403422, 0.885731), (11.419062, 0.876406),
                       (11.434284, 0.866301), (11.449057, 0.855424), (11.46335, 0.843782), (11.477129, 0.831382),
                       (11.490363, 0.818233), (11.50302, 0.80434), (11.515067, 0.789713), (11.526474, 0.774358),
                       (11.537207, 0.758282), (11.546715, 0.741402), (11.555275, 0.724247), (11.562896, 0.706849),
                       (11.569586, 0.689239), (11.575352, 0.671449), (11.580203, 0.653511), (11.584145, 0.635458),
                       (11.587187, 0.61732), (11.589337, 0.59913), (11.590602, 0.58092), (11.590991, 0.562722),
                       (11.59051, 0.544567), (11.589168, 0.526488), (11.586973, 0.508516), (11.583932, 0.490683),
                       (11.580054, 0.473021), (11.575345, 0.455562), (11.569814, 0.438338), (11.563468, 0.421381),
                       (11.556316, 0.404722), (11.548365, 0.388394), (11.539623, 0.372428), (11.530098, 0.356857),
                       (11.519798, 0.341711), (11.508729, 0.327024), (11.496901, 0.312826), (11.484321, 0.299151),
                       (11.470996, 0.286029), (11.456935, 0.273492), (11.442146, 0.261573), (11.426635, 0.250304),
                       (11.410411, 0.239716), (11.353514, 0.205578), (11.210531, 0.123768), (11.065373, 0.046092),
                       (10.91813, -0.027409), (10.768894, -0.096695), (10.617754, -0.161724), (10.464802, -0.222456),
                       (10.310128, -0.278852), (10.153823, -0.330869), (9.998891, -0.378674), (9.843078, -0.423027),
                       (9.686443, -0.46392), (9.529044, -0.501346), (9.370937, -0.535296), (9.212181, -0.565763),
                       (9.052833, -0.592738), (8.892952, -0.616215), (8.732595, -0.636185), (8.571821, -0.65264),
                       (8.410686, -0.665572), (8.249249, -0.674974), (8.087567, -0.680838), (7.925698, -0.683156),
                       (7.763701, -0.68192), (7.601633, -0.677122), (7.450187, -0.670355), (7.298992, -0.660167),
                       (7.148105, -0.646563), (6.997584, -0.629551), (6.847487, -0.609138), (6.697871, -0.585332),
                       (6.548793, -0.55814), (6.400312, -0.527568), (6.278544, -0.499551), (6.157691, -0.469249),
                       (6.038666, -0.436813), (5.980126, -0.419842), (5.922385, -0.402396), (5.908276, -0.397631),
                       (5.894461, -0.392337), (5.880947, -0.386528), (5.867747, -0.380216), (5.854869, -0.373417),
                       (5.842324, -0.366142), (5.830122, -0.358407), (5.818272, -0.350223), (5.806784, -0.341605),
                       (5.795669, -0.332566), (5.784937, -0.323119), (5.774597, -0.313279), (5.764659, -0.303058),
                       (5.755134, -0.29247), (5.746031, -0.281529), (5.73736, -0.270248), (5.729131, -0.25864),
                       (5.721355, -0.246719), (5.714041, -0.234499), (5.707198, -0.221992), (5.700838, -0.209214),
                       (5.69497, -0.196176), (5.689604, -0.182892), (5.684749, -0.169377), (5.680417, -0.155643),
                       (5.676617, -0.141703), (5.673358, -0.127573), (5.670651, -0.113264), (5.668506, -0.09879),
                       (5.666932, -0.084166), (5.66594, -0.069404), (5.66554, -0.054517), (3.830238, -0.054517),
                       (3.836231, -0.296343), (3.854102, -0.536529), (3.883683, -0.774673), (3.92481, -1.010376),
                       (3.977317, -1.243239), (4.041038, -1.472862), (4.091459, -1.625251), (5.341781, -1.625251),
                       (5.342045, -1.606965), (5.342852, -1.58857), (5.344388, -1.57034), (5.349601, -1.534447),
                       (5.357581, -1.499417), (5.368228, -1.465383), (5.38144, -1.432476), (5.397117, -1.400828),
                       (5.415157, -1.370572), (5.435459, -1.34184), (5.457922, -1.314764), (5.482445, -1.289476),
                       (5.508925, -1.266107), (5.537263, -1.24479), (5.567358, -1.225658), (5.599107, -1.208841),
                       (5.632409, -1.194473), (5.649612, -1.188248), (5.667165, -1.182684), (5.683157, -1.178397),
                       (5.699255, -1.174681), (5.715443, -1.171537), (5.731706, -1.168965), (5.74803, -1.166964),
                       (5.764399, -1.165535), (5.780799, -1.164677), (5.797213, -1.164391), (5.813627, -1.164677),
                       (5.830026, -1.165535), (5.846395, -1.166964), (5.862719, -1.168964), (5.878983, -1.171537),
                       (5.895171, -1.174681), (5.911269, -1.178396), (5.927261, -1.182684), (6.140418, -1.238767),
                       (6.247529, -1.265437), (6.301152, -1.278029), (6.354794, -1.289973), (6.500858, -1.318836),
                       (6.647429, -1.344746), (6.794461, -1.367699), (6.941909, -1.387689), (7.08973, -1.40471),
                       (7.237879, -1.418756), (7.38631, -1.429822), (7.534979, -1.437903), (7.664962, -1.444249),
                       (7.795001, -1.448783), (7.925078, -1.451503), (8.055173, -1.452409), (8.185268, -1.451503),
                       (8.315345, -1.448783), (8.445384, -1.444249), (8.575366, -1.437903), (8.700187, -1.429508),
                       (8.824856, -1.419327), (8.949353, -1.407363), (9.073661, -1.393616), (9.197758, -1.378091),
                       (9.321627, -1.360788), (9.445248, -1.34171), (9.568602, -1.320859), (9.745144, -1.28883),
                       (9.92071, -1.25226), (10.095213, -1.211174), (10.268565, -1.165596), (10.440681, -1.11555),
                       (10.611473, -1.06106), (10.780854, -1.002149), (10.948738, -0.938843), (11.032352, -0.903022),
                       (11.115334, -0.865807), (11.197665, -0.827206), (11.27933, -0.787228), (11.360311, -0.745883),
                       (11.440591, -0.703178), (11.520151, -0.659122), (11.598976, -0.613724), (11.594102, -0.621851),
                       (11.620829, -0.606802), (11.648282, -0.593692), (11.676362, -0.582523), (11.70497, -0.573296),
                       (11.734005, -0.566012), (11.76337, -0.560674), (11.792964, -0.557283), (11.822688, -0.55584),
                       (11.852443, -0.556347), (11.882129, -0.558806), (11.911647, -0.563218), (11.940897, -0.569584),
                       (11.969781, -0.577907), (11.998198, -0.588187), (12.02605, -0.600427), (12.053237, -0.614628),
                       (12.066485, -0.622426), (12.079405, -0.630629), (12.09199, -0.639226), (12.104234, -0.648208),
                       (12.116131, -0.657563), (12.127675, -0.667281), (12.138859, -0.677351), (12.149677, -0.687761),
                       (12.160123, -0.698502), (12.17019, -0.709563), (12.179873, -0.720933), (12.189166, -0.7326),
                       (12.198061, -0.744555), (12.206553, -0.756787), (12.214635, -0.769284), (12.222302, -0.782037),
                       (12.229547, -0.795033), (12.236364, -0.808264), (12.242746, -0.821717), (12.248688, -0.835382),
                       (12.254183, -0.849249), (12.259225, -0.863306), (12.263808, -0.877543), (12.267925, -0.89195),
                       (12.271571, -0.906514), (12.274738, -0.921226), (12.277421, -0.936075), (12.279614, -0.95105),
                       (12.281311, -0.96614), (12.282504, -0.981335), (12.283188, -0.996624), (12.283357, -1.011996),
                       (12.283332, -1.024188), (12.283154, -1.03638), (12.282672, -1.048572), (12.282268, -1.054668),
                       (12.281732, -1.060764), (12.281043, -1.06686), (12.280182, -1.072956), (12.279131, -1.079052),
                       (12.277871, -1.085148), (12.276382, -1.091244), (12.274645, -1.09734), (12.272642, -1.103435),
                       (12.270352, -1.109531), (12.26439, -1.133421), (12.257178, -1.156827), (12.248747, -1.17971),
                       (12.239129, -1.202025), (12.228357, -1.223731), (12.216462, -1.244786), (12.203477, -1.265148),
                       (12.189432, -1.284775), (12.174359, -1.303624), (12.158292, -1.321654), (12.141261, -1.338823),
                       (12.123298, -1.355088), (12.104435, -1.370407), (12.084705, -1.384738), (12.064139, -1.398039),
                       (12.042768, -1.410268), (11.917806, -1.480504), (11.791216, -1.54762), (11.663055, -1.61159),
                       (11.533383, -1.672388), (11.402258, -1.729986), (11.26974, -1.784358), (11.135887, -1.835477),
                       (11.000758, -1.883317), (10.667349, -1.987713), (10.330562, -2.079189), (9.990774, -2.157681),
                       (9.648362, -2.223123), (9.303702, -2.275453), (8.95717, -2.314604), (8.609144, -2.340513),
                       (8.259999, -2.353115), (8.11762, -2.356312), (7.975231, -2.357375), (7.832859, -2.356305),
                       (7.690526, -2.353102), (7.548258, -2.347767), (7.406078, -2.340301), (7.26401, -2.330705),
                       (7.122079, -2.318979), (6.988478, -2.306598), (6.855138, -2.29194), (6.722088, -2.275009),
                       (6.589356, -2.25581), (6.456971, -2.234347), (6.324962, -2.210625), (6.193359, -2.184648),
                       (6.062189, -2.15642), (5.956422, -2.131324), (5.851265, -2.104399), (5.798915, -2.090061),
                       (5.746718, -2.075037), (5.694673, -2.059251), (5.642781, -2.042626), (5.62559, -2.03639),
                       (5.608781, -2.029503), (5.592366, -2.021983), (5.576358, -2.013847), (5.560768, -2.005113),
                       (5.545609, -1.995798), (5.530892, -1.985919), (5.51663, -1.975495), (5.502834, -1.964543),
                       (5.489517, -1.953079), (5.47669, -1.941122), (5.464367, -1.928689), (5.452558, -1.915798),
                       (5.441276, -1.902465), (5.430533, -1.888709), (5.420341, -1.874547), (5.410713, -1.859995),
                       (5.401659, -1.845073), (5.393192, -1.829797), (5.385325, -1.814185), (5.378069, -1.798254),
                       (5.371436, -1.782021), (5.365439, -1.765505), (5.360089, -1.748722), (5.355399, -1.731691),
                       (5.35138, -1.714428), (5.348045, -1.69695), (5.345405, -1.679277), (5.343474, -1.661424),
                       (5.342262, -1.643409), (5.341781, -1.625251), (4.091459, -1.625251), (4.115809, -1.698845),
                       (4.201462, -1.920788), (4.297833, -2.138292), (4.404757, -2.350956), (4.522067, -2.558382),
                       (4.649598, -2.760169), (4.787184, -2.955917), (4.93466, -3.145228), (5.091861, -3.327701),
                       (5.25862, -3.502936), (5.433855, -3.669695), (5.616328, -3.826896), (5.805639, -3.974372),
                       (6.001387, -4.111958), (6.203174, -4.239489), (6.4106, -4.356799), (6.623264, -4.463722),
                       (6.840768, -4.560093), (7.06271, -4.645747), (7.288693, -4.720517), (7.518316, -4.784238),
                       (7.751178, -4.836745), (7.986882, -4.877872), (8.225026, -4.907453), (8.465211, -4.925324),
                       (8.707038, -4.931317)]

def remap(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def generate(canvas: str, color: str, **kwargs):
	profiler = Profiler()
	profiler.start()

	URL = f"https://scannables.scdn.co/uri/plain/svg/ffffff/black/1024/{kwargs['code']}"
	response = requests.get(URL)
	if response.status_code >= 400:
		raise InvalidURISpotifyGeneratorException(
			"Invalid code" if response.status_code == 400 else "Error while retrieving the code from scannables.scdn.co")

	profiler.log_event_finished("scannables_cdn_download")

	svg_without_rect = re.sub(r'<rect .+fill="#ffffff".+>\n', "", response.text)
	svg_only_code = re.sub(r'<g .+g>\n', "", svg_without_rect)

	profiler.log_event_finished("code_processing")

	pcb = tools.kicad.defaults.default()
	pcb.add_child(PcbNetNode(0, ""))
	pcb.add_child(PcbNetNode(1, "GND"))

	# Keychain
	code_start_x = 1 if kwargs["draw_spotify_logo"] else -10  # mm
	tag_half_height = 6.25
	tag_hole_diameter = 4
	copper_fill_half_height = tag_half_height + 2

	code = PcbGraphicsSvgNode(io.StringIO(svg_only_code), code_start_x, -7.5, 0.15, "F.Mask")
	pcb.add_child(code)

	tag_length = code.last_x - tag_half_height / 2

	if kwargs["draw_spotify_logo"]:
		logo = PcbGraphicsPolyNode(SPOTIFY_LOGO_POINTS, 0.048, "F.Mask", fill="solid")
		pcb.add_child(logo)

	pcb.add_child(PcbGraphicsLineNode(0, +tag_half_height, tag_length, +tag_half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsLineNode(0, -tag_half_height, tag_length, -tag_half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsArcNode(0, +tag_half_height, -tag_half_height, 0, 0, -tag_half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbGraphicsArcNode(tag_length, -tag_half_height, tag_length + tag_half_height, 0, tag_length, tag_half_height, 0.254, "Edge.Cuts"))
	pcb.add_child(PcbViaNode(0, 0, tag_hole_diameter + 0.25, tag_hole_diameter, ["F.Cu", "B.Cu"], 1))

	copper_fill_path = Path()
	copper_fill_path.append(CubicBezier(complex(0, -tag_half_height), complex(-tag_half_height * 1.35, -tag_half_height), complex(-tag_half_height * 1.35, +tag_half_height), complex(0, tag_half_height), ))
	copper_fill_path.append(Line(complex(0, tag_half_height), complex(tag_length, tag_half_height), ))
	copper_fill_path.append(CubicBezier(complex(tag_length, tag_half_height), complex(tag_length + tag_half_height * 1.35, +tag_half_height), complex(tag_length + tag_half_height * 1.35, -tag_half_height), complex(tag_length, -tag_half_height)))
	copper_fill_path.append(Line(complex(tag_length, -tag_half_height), complex(0, -tag_half_height), ))

	copper_fill_polygon = []
	for i in range(250):
		cp = copper_fill_path.point(i / (250 - 1))
		copper_fill_polygon.append((cp.real, cp.imag))

	k = PcbZoneNode(
		[(tag_length + copper_fill_half_height, copper_fill_half_height), (-copper_fill_half_height, copper_fill_half_height), (-copper_fill_half_height, -copper_fill_half_height), (tag_length + copper_fill_half_height, -copper_fill_half_height) ],
		[{"layer": "F.Cu", "points": copper_fill_polygon}, {"layer": "B.Cu", "points": copper_fill_polygon}, ],
		1, "GND",
		"F&B.Cu"
	)
	pcb.add_child(k)

	profiler.log_event_finished("pcb_generation")

	stream = io.StringIO()
	pcb.write(stream)
	kicad_pcb_content = stream.getvalue()

	profiler.log_event_finished("pcb_to_kicad_export")

	with tempfile.NamedTemporaryFile(suffix=".kicad_pcb", delete=False) as kicad_pcb_file:
		kicad_pcb_file.write(kicad_pcb_content.encode("utf-8"))

	profiler.log_event_finished("pcb_to_kicad_export_saved")

	svgs = pcb2svg.generate_svg_from_gerber_and_drill(kicad_pcb_file.name)
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

		# svgs = gerber2svg.generate_svg_from_gerber_and_drill(
		# 	gerber_dir=tmp_dir,
		# 	theme=color
		# )
		#
		# profiler.log_event_finished("gerber_to_svg_conversion")

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
		"profiler": profiler.end()
	}
