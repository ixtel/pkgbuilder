from setuptools import find_packages

from distutils.core import setup
from distutils.extension import Extension

from Cython.Distutils import build_ext
from Cython.Build import cythonize

import os
from pipreqs import pipreqs

try:
	from .config import CYTON, PCG_NAME, REQS_VERSION_STRONG, REQS, VERSION, DESCR, README, URL, AUTHOR, EMAIL, LICENSE, DATAFILES_DIR, \
		PACKAGES_EXCLUDE
except Exception as _ex:
	from config import CYTON, PCG_NAME, REQS_VERSION_STRONG, REQS, VERSION, DESCR, README, URL, AUTHOR, EMAIL, LICENSE, DATAFILES_DIR, \
		PACKAGES_EXCLUDE

HERE = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')


def _pathpkg_split(path):
	res = os.path.normpath(path).replace('\\', '/').split('/')
	if res[0] == '':
		res.pop(0)
	return res


def cython_file_list():
	files_for_cython = []
	_excl__name = '__init__' if CYTON is True else ''
	for _root, dirs, files in os.walk(os.path.join('.', PCG_NAME)):
		if _root.find('.dev') > -1:
			continue
		__root = _pathpkg_split(_root)
		print('cython_file_list root', _root, 'dirs', dirs, 'files', files, '_root', __root)
		for file in files:
			_name, _ext = os.path.splitext(file.lower().replace('\\', '/'))
			if _ext == '.py' and _excl__name != _name and _root != '.':
				_path = __root + [_name, _ext]
				files_for_cython.append(_path)
	return files_for_cython


def ext_pack_namelist(namelist):
	d, p = '.'.join(namelist[:-1]), '/'.join(namelist[:-1]) + namelist[-1]
	return d.replace('\\', '/'), p.replace('\\', '/')


def get_extension():
	files = cython_file_list()
	ext_modules = []
	for f in files:
		ext, module = ext_pack_namelist(f)
		print('>> Add to compile ext', ext, 'module', module)
		ext_module = Extension(ext, [module])
		ext_modules.append(ext_module)
	return ext_modules


def get_requires():
	pkgs = pipreqs.get_all_imports(os.path.join(HERE, PCG_NAME), encoding='utf-8')
	print('pkgs', pkgs)
	pkgs_filtred = list(set(pkgs) - set(PACKAGES_EXCLUDE))
	print('pkgs_filtred', pkgs_filtred)
	candidates = pipreqs.get_pkg_names(pkgs_filtred)
	print('candidates', candidates)
	local = pipreqs.get_import_local(candidates)
	print('local', local)
	difference = [x for x in candidates if x.lower() not in [z['name'].lower() for z in local]]
	imports = local + pipreqs.get_imports_info(difference)
	print('<< imports==', imports)
	fmt = '{name}=={version}'
	res = [
		fmt.format(**item) if item['version'] and REQS_VERSION_STRONG else '{name}'.format(**item) for item in imports
	]
	print('res', res)
	return res


def get_data_files(paths):
	data_files = []
	if paths:
		for path, ext in paths:
			start_point = os.path.join(PCG_NAME, path)
			for root, dirs, files in os.walk(start_point):
				root_files = [os.path.join(root, i).replace('\\', '/') for i in files if os.path.splitext(i)[1][1:] == ext or ext == '*']
				data_files.append((os.path.join('lib', 'site-packages', root).replace('\\', '/'), root_files))
	return data_files


if __name__ == '__main__':
	options = {}
	if CYTON is True:
		options['cmdclass'] = {'build_ext': build_ext}
	
	if REQS is True:
		options['install_requires'] = get_requires()
	
	if CYTON is True:
		options['ext_modules'] = cythonize(get_extension(), compiler_directives=dict(always_allow_keywords=True, language_level="3"))
	else:
		options['packages'] = find_packages()
	
	options.update(dict(
		name=PCG_NAME,
		version=VERSION,
		description=DESCR,
		long_description=README,
		url=URL,
		author=AUTHOR,
		author_email=EMAIL,
		license=LICENSE,
		classifiers=[
			'Development Status :: 3 - Alpha',
			'Intended Audience :: Developers',
			'Topic :: Software Development :: Build Tools',
			'License :: OSI Approved :: MIT License',
			'Programming Language :: Python :: 3',
		],
		keywords=PCG_NAME,
		data_files=get_data_files(DATAFILES_DIR),
	))
	setup(**options)
