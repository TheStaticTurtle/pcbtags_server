import git

def get_last_commit_short_hash():
	try:
		repo = git.Repo(search_parent_directories=True)
		if repo.is_dirty():
			return repo.head.object.hexsha[:8] + "-dirty"
		return repo.head.object.hexsha[:8]
	except git.GitError:
		return "untracked"
