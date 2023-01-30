import sys

from .builder import BuiderPKG

ARGS = (
	'cyton',
	'sdist',
	'build',
	'pack',
	'release',
	'clean',
	'packlasts',
	'buildcopy',
	'reqs',
	'reqs_version_strong',
	'install',
)


def build_options(args):
	options = {}
	for arg in ARGS:
		options[arg] = arg in args
	return options


def worker(pkg_name, cyton, release, build, pack, clean, sdist, packlasts, buildcopy, reqs, reqs_version_strong, install, packages_path):
	b = BuiderPKG(pkg_name, cyton, buildcopy, reqs, reqs_version_strong, packages_path=packages_path)
	print('init BuiderPKG')
	if release:
		build = True
		pack = True
	if build:
		b.build_release(sdist)
	# TODO if buildcopy is False:
	if pack:
		b.build_instance()
	if clean:
		b.clean_build_dir()
	if packlasts:
		b.copy_last_to_projectsdir()
	if install:
		b.install_last()


def build_package(pkg_name, args):
	print('run main')
	_args = args.split('packages_path=')
	packages_path = None
	if len(_args) > 1:
		packages_path = _args[1]
		_args = _args[0].split(' ')
	options = build_options(_args)
	options['packages_path'] = packages_path
	print(options)
	worker(pkg_name, **options)


if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1]:
		build_package(*sys.argv)
