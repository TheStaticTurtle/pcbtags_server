import tools.git_tool


VERSION = f"0.0.1-{tools.git_tool.get_last_commit_short_hash()}"

CACHE_TIME_MINUTES = 1440

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
