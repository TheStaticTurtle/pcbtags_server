import os
import tools.git_tool

VERSION = f"1.0.0-{tools.git_tool.get_last_commit_short_hash()}"

CACHE_TIME_MINUTES = os.getenv('CACHE_TIME_MINUTES', 1440)

REDIS_HOST = os.getenv('REDIS_HOST', 'pcbtags-cache')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 0)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
