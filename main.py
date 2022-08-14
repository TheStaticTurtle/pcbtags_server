import sys
import typing
import traceback

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

import config
import tools.kicad.pcb2svg
from tools.profiler import Profiler
from generators.exception import GeneratorException

import generators.spotify
import generators.nametag

app = FastAPI()

enabled_generators = [
	generators.spotify,
	generators.nametag
]

@app.get("/api/version")
async def generators():
	return {
		"detail": "success",
		"data": config.VERSION
	}

@app.get("/api/generators")
async def generators():
	return {
		"detail": "success",
		"data": [
			{
				"name": generator.TEXT,
				"key": generator.KEY,
				"desc": generator.DESC,
				"short_desc": generator.SHORT_DESC,
				"available_canvases": generator.AVAILABLE_CANVASES,
				"options": generator.OPTIONS,
			}
			for generator in enabled_generators
		]
	}

@app.get("/api/pcb_colors")
async def pcb_colors():
	return {
		"detail": "success",
		"data": tools.kicad.pcb2svg.THEMES
	}


class GenerateModel(BaseModel):
	color: str
	canvas: str
	options: typing.Dict

@app.post("/api/generators/{generator_key}", status_code=200)
async def generate(generator_key: str, options: GenerateModel, response: Response):
	generator = None
	for g in enabled_generators:
		if g.KEY == generator_key:
			generator = g

	if generator is None:
		response.status_code = status.HTTP_400_BAD_REQUEST
		return {"detail": f"Generator \"{generator_key}\" does not exist"}

	try:
		profiler = Profiler()
		profiler.start()
		data = generator.generate(options.canvas, options.color, profiler, **options.options)
		data["profiler"] = profiler.end()
		return {
			"detail": f"success",
			"data": data
		}
	except GeneratorException as e:
		response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
		tb = traceback.format_exc()
		sys.stderr.write(tb)
		return {"detail": f"A generator exception occurred while trying to generate the design.", "real_error": str(e), "traceback": tb}
	except Exception as e:
		response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
		tb = traceback.format_exc()
		sys.stderr.write(tb)
		return {"detail": f"A unknown fatal exception occurred.", "real_error": str(e), "traceback": tb}
