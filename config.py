import tools.git_tool


VERSION = f"0.0.1-{tools.git_tool.get_last_commit_short_hash()}"
