import hashlib
import json
import sys
import typing
import traceback
from datetime import timedelta

import redis as pyredis
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

import config
import tools.kicad.pcb2svg
from tools.profiler import Profiler
from generators.exception import GeneratorException

import generators.spotify
import generators.nametag

redis = pyredis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)
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
				"caching_allowed": generator.CACHING_ALLOWED,
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


class GenerateOptionModel(BaseModel):
	color: str
	canvas: str
	options: typing.Dict

	def hash(self):
		h = hashlib.new('sha256')
		h.update((self.color+"+"+self.canvas+"+"+json.dumps(self.options)).encode("utf8"))
		return h.hexdigest()

@app.post("/api/generators/{generator_key}", status_code=200)
async def generate(generator_key: str, options: GenerateOptionModel, response: Response):
	profiler = Profiler()
	profiler.start()

	generator = None
	for g in enabled_generators:
		if g.KEY == generator_key:
			generator = g

	if generator is None:
		response.status_code = status.HTTP_400_BAD_REQUEST
		return {"detail": f"Generator \"{generator_key}\" does not exist"}

	try:
		options_hash = options.hash()
		cached_data = None
		if generator.CACHING_ALLOWED:
			cached_data = redis.get(options_hash)

		if cached_data:
			data = json.loads(cached_data)
			profiler.log_event("cache_loaded", facility="cache")

			for event in data["profiler"]["events"]:
				profiler.log_event(event['name'], cached=True, facility=event['facility'])

		else:
			data = generator.generate(options.canvas, options.color, profiler, **options.options)
			data["profiler"] = profiler.__dict__
			if generator.CACHING_ALLOWED:
				state = redis.setex(options_hash, timedelta(minutes=config.CACHE_TIME_MINUTES), value=json.dumps(data).encode("utf8"))
				profiler.log_event("cache_saved", facility="cache")

		profiler.end()
		data["profiler"] = profiler.__dict__
		return {
			"detail": f"success",
			"data": data,
			"cached": cached_data is not None
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
