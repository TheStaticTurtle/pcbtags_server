from .main import generate
import tools.models.data

INFOS = tools.models.data.GeneratorInfo(
	key="spotify_tag",
	name="Spotify tag",
	caching_allowed=True,

	short_desc="Generate a keychain sized tag with a spotify code on the front",
	desc="Generate a keychain sized tag with a spotify code on the front",

	available_canvases=[
		tools.models.data.GeneratorCanvas(
			key="keychain",
			text="Keychain",
			size_min=tools.models.data.GeneratorCanvasSize(
				height=12.5,
				width=42.5,
			),
			size_max=tools.models.data.GeneratorCanvasSize(
				height=12.5,
				width=67.37,
			),
			help="",
		)
	],

	options=[
		tools.models.data.GeneratorOption(
			type="String",
			key="code",
			text="Spotify URI / Share URL",
			default="spotify:track:4cOdK2wGLETKBW3PvgPWqT",
			help="You might need to remove the \"?si=xxxxxxxxxxxx\" part of the URL or add your username in the URI \"spotify:user:xxxxxxxx:playlist:xxxxxxxxx\"",
		),
		tools.models.data.GeneratorOption(
			type="Boolean",
			key="draw_spotify_logo",
			text="Draw spotify logo",
			default=True,
			help="",
		),
		tools.models.data.GeneratorOption(
			type="Boolean",
			key="add_keychain_hole",
			text="Add the keychain hole",
			default=True,
			help="",
		),
	],
)