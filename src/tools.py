import subprocess
import os
import shutil


def path_dir(path):
	return os.path.dirname(path).replace('\\', '/')


def path_abs(path):
	return os.path.abspath(path).replace('\\', '/')


def path_join(*args):
	return os.path.join(*args).replace('\\', '/')


def copy_set(name, p1, p2):
	return (
		path_join(p1, name),
		path_join(p2, name)
	)


def get_files_from_dir(path='.'):
	r = [f.name for f in os.scandir(path) if f.is_file()]
	return r


def copytree(src, dst, symlinks=False, ignore=None):
	if ignore is None:
		ignore = []
	if not os.path.exists(dst):
		os.makedirs(dst)
	for item in os.listdir(src):
		if item != '__pycache__':
			s = path_join(src, item)
			d = path_join(dst, item)
			if item not in ignore:
				if os.path.isdir(s):
					copytree(s, d, symlinks, ignore)
				else:
					if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
						shutil.copy2(s, d)
	return None


def install_dist(path='./.last'):
	print('path', path)
	files = get_files_from_dir(path)
	cmd = 'pip install {} -U --no-deps --force-reinstall'
	for file in files:
		_cmd = cmd.format(path + '/' + file)
		print('>> _cmd', _cmd)
		try:
			subprocess.run(_cmd, shell=True)
		except Exception as ex:
			print('Exception', ex)
