from .main import generate
import tools.models.data

INFOS = tools.models.data.GeneratorInfo(
	key="nametag",
	name="Nametag",
	caching_allowed=False,

	short_desc="Simple nametag with a QRCODE containing contact infos",
	desc="Simple nametag with a QRCODE containing contact infos",

	available_canvases=[
		tools.models.data.GeneratorCanvas(
			key="keychain",
			text="Keychain",
			size_min=tools.models.data.GeneratorCanvasSize(
				height=12.5,
				width=14.5,
			),
			size_max=tools.models.data.GeneratorCanvasSize(
				height=12.5,
				width=None,
			),
			help="",
		)
	],

	options=[
		tools.models.data.GeneratorOption(
			type="String",
			key="lastname",
			text="Lastname",
			default="DOE",
			help="",
		),
		tools.models.data.GeneratorOption(
			type="String",
			key="firstname",
			text="Firstname",
			default="John",
			help="",
		),
		tools.models.data.GeneratorOption(
			type="String",
			key="email",
			text="E-Mail",
			default="johndoe@gmail.com",
			help="",
		),
		tools.models.data.GeneratorOption(
			type="String",
			key="phone",
			text="Phone number",
			default="+33 XXXXXXXXX",
			help="",
		),
		tools.models.data.GeneratorOption(
			type="Boolean",
			key="draw_qrcode",
			text="Draw QRCode",
			default=True,
			help="QRCode might not be readable or able the generate if there is too much information or the code is to fine to be printable",
		),
		tools.models.data.GeneratorOption(
			type="Boolean",
			key="add_keychain_hole",
			text="Add the keychain hole",
			default=True,
			help="",
		),
	]
)