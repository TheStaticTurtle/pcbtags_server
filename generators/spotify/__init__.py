from .main import generate

TEXT = "Spotify tag"
KEY = "spotify_tag"
AVAILABLE_CANVASES = [
	{"key": "keychain", "text": "Keychain"}
]
OPTIONS = [
	{"type": "String", "key": "code", "text": "Music / Playlist URI", "default": "spotify:track:4cOdK2wGLETKBW3PvgPWqT"},
	{"type": "Boolean", "key": "draw_spotify_logo", "text": "Draw spotify logo", "default": True},
	{"type": "Boolean", "key": "add_keychain_hole", "text": "Add the keychain hole", "default": True}
]
