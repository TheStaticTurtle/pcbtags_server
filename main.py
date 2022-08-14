import json
import sys

import traceback
from datetime import timedelta

import redis as pyredis
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

import config
import tools.kicad.pcb2svg
from tools.profiler import Profiler
from generators.exception import GeneratorException

import tools.models.api
import tools.models.data

import generators.spotify
import generators.nametag

redis = pyredis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)
app = FastAPI(
	title="PCBTAGS",
	description="Api for generating pcb based tags",
	version=config.VERSION
)

enabled_generators = [
	generators.spotify,
	generators.nametag
]


@app.get("/api/version", response_model=tools.models.api.ApiVersionResponse)
async def version():
	response = tools.models.api.ApiVersionResponse(
		version=config.VERSION
	)
	return response

@app.get("/api/generators", response_model=tools.models.api.ApiGeneratorsResponse)
async def generators():
	response = tools.models.api.ApiGeneratorsResponse(
		generators=[generator.INFOS for generator in enabled_generators]
	)
	return response

@app.get("/api/pcb_colors", response_model=tools.models.api.ApiPcbColorsResponse)
async def pcb_colors():
	response = tools.models.api.ApiPcbColorsResponse(
		colors=tools.kicad.pcb2svg.THEMES
	)
	return response


@app.post(
	"/api/generators/{generator_key}",
	status_code=200,
	response_model=tools.models.api.ApiGeneratedDataResponse,
	responses={
		404: {"model": tools.models.api.BaseApiResponse},
		400: {"model": tools.models.api.BaseApiResponse},
		500: {"model": tools.models.api.BaseApiResponse},
	}
)
async def generate(generator_key: str, options: tools.models.api.ApiGenerateParamsModel):
	profiler = Profiler()
	profiler.start()

	generator = None
	for g in enabled_generators:
		if g.INFOS.key == generator_key:
			generator = g

	if generator is None:
		return JSONResponse(
			status_code=status.HTTP_400_BAD_REQUEST,
			content=tools.models.api.BaseApiResponse(
				error=tools.models.data.ErrorModel(
					short_text=f"Selected generator ({generator_key}) does not exist",
					traceback=None,
				)
			).dict()
		)

	try:
		options_hash = options.hash()
		response_was_cached = False
		data = None

		if generator.INFOS.caching_allowed:
			cached_data = redis.get(options_hash)
			if cached_data:
				try:
					data = json.loads(cached_data)
					data = tools.models.data.PcbExportedData(
						**data
					)

					response_was_cached = True
					profiler.log_event("cache_loaded", facility="cache")

					for event in data.profiler["events"]:
						profiler.log_event(event['name'], cached=True, facility=event['facility'])
				except Exception as e:
					profiler.log_event("cache_load_failed", facility="cache")
					print(e)

		if not response_was_cached or data is None:
			data = generator.generate(options.canvas, options.color, profiler, **options.options)
			data.profiler = profiler.__dict__

			if generator.INFOS.caching_allowed:
				if not redis.setex(options_hash, timedelta(minutes=config.CACHE_TIME_MINUTES), value=data.json()):
					print("Failed to save to cache")
				profiler.log_event("cache_saved", facility="cache")

		profiler.end()
		data.profiler = profiler.__dict__
		return tools.models.api.ApiGeneratedDataResponse(
			result=data,
			response_cached=response_was_cached,
		)

	except GeneratorException as e:
		tb = traceback.format_exc()
		sys.stderr.write(tb)
		return JSONResponse(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			content=tools.models.api.BaseApiResponse(
				error=tools.models.data.ErrorModel(
					short_text=str(e),
					traceback=tb,
				)
			).dict()
		)
	except Exception as e:
		tb = traceback.format_exc()
		sys.stderr.write(tb)
		return JSONResponse(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			content=tools.models.api.BaseApiResponse(
				error=tools.models.data.ErrorModel(
					short_text=str(e),
					traceback=tb,
				)
			).dict()
		)
