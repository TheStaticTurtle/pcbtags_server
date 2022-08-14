import hashlib
import typing
from pydantic import BaseModel
import json

from .data import ErrorModel, GeneratorInfo, PcbColor, PcbExportedData

class BaseApiResponse(BaseModel):
	error: typing.Optional[ErrorModel]


class ApiVersionResponse(BaseApiResponse):
	version: str


class ApiGeneratorsResponse(BaseApiResponse):
	generators: typing.List[GeneratorInfo]


class ApiPcbColorsResponse(BaseApiResponse):
	colors: typing.List[PcbColor]


class ApiGenerateParamsModel(BaseModel):
	color: str
	canvas: str
	options: typing.Dict

	def hash(self):
		h = hashlib.new('sha256')
		h.update((self.color+"+"+self.canvas+"+"+json.dumps(self.options)).encode("utf8"))
		return h.hexdigest()


class ApiGeneratedDataResponse(BaseApiResponse):
	result: PcbExportedData
	response_cached: bool
