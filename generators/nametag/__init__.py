from .main import generate

TEXT = "Nametag"
KEY = "nametag"
SHORT_DESC = "Simple nametag with a QRCODE containing contact infos"
DESC = SHORT_DESC
AVAILABLE_CANVASES = [
	{
		"key": "keychain",
		"text": "Keychain",
		"size_max": {
			"height": 12.5,
			"width": "indeterminate ",
		},
		"help": ""
	}
]
OPTIONS = [
	{
		"type": "String",
		"key": "lastname",
		"text": "Lastname",
		"default": "DOE",
		"help": "",
	},
	{
		"type": "String",
		"key": "firstname",
		"text": "Firstname",
		"default": "John",
		"help": "",
	},
	{
		"type": "String",
		"key": "email",
		"text": "E-Mail",
		"default": "johndoe@gmail.com",
		"help": "",
	},
	{
		"type": "String",
		"key": "phone",
		"text": "Phone number",
		"default": "+33 XXXXXXXXX",
		"help": "",
	},
	{
		"type": "Boolean",
		"key": "draw_qrcode",
		"text": "Draw QRCode",
		"default": True,
		"help": "QRCode might not be readable or able the generate if there is too much information or the code is to fine to be printable",
	},
	{
		"type": "Boolean",
		"key": "add_keychain_hole",
		"text": "Add the keychain hole",
		"default": True,
		"help": "",
	}
]
