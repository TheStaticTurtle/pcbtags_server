from generators.exception import GeneratorException


class SpotifyGeneratorException(GeneratorException):
	pass

class InvalidURISpotifyGeneratorException(GeneratorException):
	pass

class ScannablesCDNSpotifyGeneratorException(InvalidURISpotifyGeneratorException):
	pass

class SVGCodeSpotifyGeneratorException(GeneratorException):
	pass
