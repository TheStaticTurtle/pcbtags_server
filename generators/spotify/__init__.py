from .main import generate

CACHING_ALLOWED = True
TEXT = "Spotify tag"
KEY = "spotify_tag"
SHORT_DESC = "Generate a keychain sized tag with a spotify code on the front"
DESC = SHORT_DESC
AVAILABLE_CANVASES = [
	{
		"key": "keychain",
		"text": "Keychain",
		"size_max": {
			"height": 12.5,
			"width": 67.37,
		},
		"help": ""
	}
]
OPTIONS = [
	{
		"type": "String",
		"key": "code",
		"text": "Spotify URI / Share URL",
		"default": "spotify:track:4cOdK2wGLETKBW3PvgPWqT",
		"help": "You might need to remove the \"?si=xxxxxxxxxxxx\" part of the URL or add your username in the URI \"spotify:user:xxxxxxxx:playlist:xxxxxxxxx\"",
	},
	{
		"type": "Boolean",
		"key": "draw_spotify_logo",
		"text": "Draw spotify logo",
		"default": True,
		"help": "",
	},
	{
		"type": "Boolean",
		"key": "add_keychain_hole",
		"text": "Add the keychain hole",
		"default": True,
		"help": "",
	}
]
