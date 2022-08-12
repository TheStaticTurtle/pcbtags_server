from .main import generate

TEXT = "Spotify tag"
KEY = "spotify_tag"
SHORT_DESC = "Generate a keychain sized tag with a spotify code on the front"
DESC = SHORT_DESC
AVAILABLE_CANVASES = [
	{"key": "keychain", "text": "Keychain"}
]
OPTIONS = [
	{"type": "String", "key": "code", "text": "Spotify URI / Share URL", "default": "spotify:track:4cOdK2wGLETKBW3PvgPWqT"},
	{"type": "Boolean", "key": "draw_spotify_logo", "text": "Draw spotify logo", "default": True},
	{"type": "Boolean", "key": "add_keychain_hole", "text": "Add the keychain hole", "default": True}
]
