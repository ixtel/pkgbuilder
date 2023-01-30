import importlib
import os
import subprocess
import sys
import time
from shutil import rmtree, copy2
import importlib.util

from .tools import copytree, copy_set, path_abs, path_dir, path_join, get_files_from_dir

PACKAGES_LOCAL = [
	'celebro',
	'dataminer',
	'geometro',
	'ihooks',
	'iloger',
	'itools',
	'inigui',
	'interneter',
	'iparser',
	'itester',
	'itexter',
	'ithread',
	'itimer',
	'itransport',
	'parser_avito',
	'parser_google',
	'parser_habr',
	'parser_search',
	'parser_yandex',
	'pkgbuilder',
	'rewr',
	'robot_board',
	'robot_clicker',
	'seotools',
	'userface',
	'vps_setup',
]

PACKAGES_EXCLUDE = ['numpy', 'win32api', 'win32gui', 'win32con', 'win32security', 'pywin32', 'pypiwin32'] + PACKAGES_LOCAL


def module_path(name, path):
	_spec = importlib.util.spec_from_file_location(name, path)
	_module = importlib.util.module_from_spec(_spec)
	_spec.loader.exec_module(_module)
	return _module


def module_to_dict(module):
	res = {}
	for k, v in module.__dict__.items():
		if k.startswith('__'):
			continue
		else:
			if isinstance(v, str):
				if k == 'README':
					v = '"""{}"""'.format(v)
				else:
					v = '"{}"'.format(v)
			res[k] = v
	return res


def git_detect():
	git_path_vars = [
		'git',
		'c:\\cygwin\\git',
		'c:\\cygwin64\\bin\\git',
		'c:\\Program Files (x86)\\Git\\bin\\git',
		'c:\\Program Files\\Git\\bin\\git'
	]
	git_path = None
	for g in git_path_vars:
		try:
			subprocess.call([g, '--version'])
			git_path = g
			print('>> Found git at: {}'.format(git_path))
		except Exception as _ex:
			print('<< Exception', _ex, g)
			pass
	if not git_path:
		sys.exit(
			'Git not found. Please install it (http://git-scm.com/ or cygwin: \'apt-cyg install git\' or in other way)')
	return git_path


def build_git_version(ver):
	print('>> Version', ver)
	ver = ver if ver else str(int(time.time()))[5:]
	vers = list(str(ver))
	if len(vers) < 3:
		vers = ['0'] * (3 - len(vers)) + vers
	vers_sub = vers[:3]
	ver_str = '.'.join(vers_sub)
	print('>> Version reBuild', ver_str)
	return ver_str


class BuiderPKG:
	def __init__(self, pkg_name, cytonize=False, buildcopy=False, reqs=False, reqs_version_strong=False, packages_path=None):
		
		print(pkg_name, cytonize, buildcopy)
		self.HERE = path_abs(path_dir(__file__))
		
		if packages_path:
			self.PARENT = path_abs(packages_path)
		else:
			self.PARENT = path_abs(path_join(__file__, '../..'))
		
		self.PKG_DIR = path_join(self.PARENT, pkg_name)
		self.TPL_DIR = path_join(self.HERE, 'tpl')
		
		self.buildcopy = buildcopy
		
		if buildcopy is True:
			print('>> buildcopy', buildcopy)
			self.BUILD_DIR = path_join(self.PARENT, pkg_name, '..', '.build', pkg_name)
		else:
			self.BUILD_DIR = path_join(self.PARENT, pkg_name, '.build')
		
		self.CFG = module_path('config', path_join(self.PKG_DIR, 'config.py'))
		self.CFG.PACKAGES_EXCLUDE = PACKAGES_EXCLUDE
		self.CFG.CYTON = cytonize
		self.CFG.REQS = reqs
		self.CFG.REQS_VERSION_STRONG = reqs_version_strong
		self.COPYFILES = [
			copy_set('config.py', self.PKG_DIR, self.BUILD_DIR),
			copy_set('MANIFEST.in', self.TPL_DIR, self.BUILD_DIR),
			copy_set('LICENSE.txt', self.TPL_DIR, self.BUILD_DIR),
			copy_set('setup.cfg', self.TPL_DIR, self.BUILD_DIR),
			copy_set('setup.py', self.TPL_DIR, self.BUILD_DIR),
		]
		
		self.BUILD_DIST_DIR = path_join(self.BUILD_DIR, 'dist')
		self.RELEASE_DIR = path_join(self.PKG_DIR, '.release')
		self.LAST_REALESE_DIR = path_join(self.PKG_DIR, '.last')
		self.PARENT_LAST_REALESE_DIR = path_join(self.PARENT, '.last')
		
		self.PKG_BUILD_DIR = path_join(self.BUILD_DIR, self.CFG.PCG_NAME)
		self.SRC_DIR = path_join(self.PKG_DIR, self.CFG.SRC_DIR).replace('\\', '/')
		
		self.VERSION = None
		self._prepare()
		
		self.RELEASE_VERSION_DIR = path_join(self.RELEASE_DIR, self.VERSION)
		
		self.PKG_INSTANCE_DIR = ''
		self.RELEASE_LAST_INSTANCE_DIR = ''
		self.RELEASE_VERSION_INSTANCE_DIR = ''
		if self.CFG.COPYDIRS_INSTANCE:
			self.PKG_INSTANCE_DIR = path_join(self.PKG_DIR, self.CFG.COPYDIRS_INSTANCE)
			self.RELEASE_LAST_INSTANCE_DIR = path_join(self.LAST_REALESE_DIR, self.CFG.COPYDIRS_INSTANCE)
			self.RELEASE_VERSION_INSTANCE_DIR = path_join(self.RELEASE_VERSION_DIR, self.CFG.COPYDIRS_INSTANCE)
	
	# ================================================
	# ======BUILDER_INSTANCE_BEGIN====================
	
	def _prepare(self):
		print('>> Clean This DIR')
		self.clean_build_dir()
		
		print('>> Copy app files to working dir')
		self._copy_pkg_to_workdir()
		
		print('>> Copy stat files to working dir')
		self._copy_statfiles_to_workdir()
		
		print('>> Generating version')
		self._build_version()
		
		if self.VERSION is None:
			raise Exception('self.VERSION is None')
	
	def _copy_instance_to_releasedir(self):
		if self.CFG.COPYDIRS_INSTANCE:
			print('>> Clean Instance Version', self.RELEASE_VERSION_INSTANCE_DIR)
			try:
				rmtree(self.RELEASE_VERSION_INSTANCE_DIR)
			except Exception as _ex:
				print('<< Warning', _ex)
			
			print('>> Copy Instance Version', self.RELEASE_VERSION_INSTANCE_DIR)
			try:
				copytree(self.PKG_INSTANCE_DIR, self.RELEASE_VERSION_INSTANCE_DIR)
			except Exception as _ex:
				print('<< Exception', _ex)
			
			print('>> Clean Instance Last', self.RELEASE_LAST_INSTANCE_DIR)
			try:
				rmtree(self.RELEASE_LAST_INSTANCE_DIR)
			except Exception as _ex:
				print('<< Warning', _ex)
			
			print('>> Copy Instance Last', self.RELEASE_LAST_INSTANCE_DIR)
			try:
				copytree(self.PKG_INSTANCE_DIR, self.RELEASE_LAST_INSTANCE_DIR)
			except Exception as _ex:
				print('<< Exception', _ex)
	
	def _copy_pkg_to_releasedir(self):
		print('>> Clean Realese Version', self.RELEASE_VERSION_DIR)
		try:
			rmtree(self.RELEASE_VERSION_DIR)
		except Exception as _ex:
			print('<< Warning', _ex)
		
		print('>> Clean Realese Last', self.LAST_REALESE_DIR)
		try:
			rmtree(self.LAST_REALESE_DIR)
		except Exception as _ex:
			print('<< Warning', _ex)
		
		print('>> Copy Realese Version', self.RELEASE_VERSION_DIR)
		try:
			copytree(self.BUILD_DIST_DIR, self.RELEASE_VERSION_DIR)
		except Exception as _ex:
			print('<< Exception', _ex)
		
		print('>> Copy Realese Last', self.LAST_REALESE_DIR)
		try:
			copytree(self.BUILD_DIST_DIR, self.LAST_REALESE_DIR)
		except Exception as _ex:
			print('<< Exception', _ex)
	
	def copy_last_to_projectsdir(self):
		print(
			'>> Copy Realese Last TO Workdir Last',
			self.LAST_REALESE_DIR,
			self.PARENT_LAST_REALESE_DIR, sep='\n'
		)
		try:
			copytree(self.LAST_REALESE_DIR, self.PARENT_LAST_REALESE_DIR)
		except Exception as _ex:
			print('<< Exception', _ex)
	
	# ======BUILDER_INSTANCE==========================
	# ================================================
	
	# ================================================
	# ======BUILDER_BEGIN=============================
	
	def _build_version(self):
		version = self._create_version_file(path_join(self.PKG_BUILD_DIR, 'version.py'))
		self.VERSION = version
		self.CFG.VERSION = version
	
	def clean_build_dir(self):
		print('>> Clean Build', self.BUILD_DIR)
		try:
			rmtree(self.BUILD_DIR)
		except Exception as _ex:
			print('<< Warning', _ex)
		
		print('>> Clean __pycache__', path_join(self.PKG_DIR, '__pycache__'))
		try:
			rmtree(path_join(self.PKG_DIR, '__pycache__'))
		except Exception as _ex:
			print('<< Warning', _ex)
	
	def _copy_statfiles_to_workdir(self):
		for _set in self.COPYFILES:
			print('>> Copy COPYFILES', *_set, sep='\n')
			try:
				copy2(*_set)
			except Exception as _ex:
				print('<< Exception', _ex)
	
	def _copy_pkg_to_workdir(self):
		print(
			'>> Copy App',
			self.SRC_DIR,
			self.PKG_BUILD_DIR, sep='\n'
		)
		try:
			copytree(self.SRC_DIR, self.PKG_BUILD_DIR)
		except Exception as _ex:
			print('<< Exception', _ex)
	
	def _build_package(self):
		os.chdir(self.BUILD_DIR)
		print('>> build_package Change dir to', self.BUILD_DIR)
		os.system('python setup.py bdist_wheel')
	
	def _build_package_sdist(self):
		os.chdir(self.BUILD_DIR)
		print('>> build_package_sdist Change  dir to', self.BUILD_DIR)
		os.system('python setup.py sdist')
	
	def _build_manifest(self):
		try:
			with open(path_join(self.BUILD_DIR, 'MANIFEST.in'), mode='w+', encoding='utf-8') as f:
				if self.CFG.DATAFILES_DIR:
					for r in self.CFG.DATAFILES_DIR:
						f.write('recursive-include {}/{} *.{} \n'.format(self.CFG.PCG_NAME, *r))
				f.close()
		except Exception as _ex:
			print('<< Exception', _ex)
	
	def _build_config(self):
		try:
			with open(path_join(self.BUILD_DIR, 'config.py'), mode='a', encoding='utf-8') as f_out:
				f_out.write(f'\n')
				f_out.write(f'CYTON = {self.CFG.CYTON}\n')
				f_out.write(f'REQS_VERSION_STRONG = {self.CFG.REQS_VERSION_STRONG}\n')
				f_out.write(f'REQS = {self.CFG.REQS}\n')
				f_out.write(f"VERSION = '{self.VERSION}'\n")
				f_out.write(f'PACKAGES_EXCLUDE = {self.CFG.PACKAGES_EXCLUDE}\n')
				f_out.close()
		except Exception as _ex:
			print('<< Exception', _ex)
	
	# ======BUILDER_END===============================
	# ================================================
	
	# ================================================
	# ======VERSION_BEGIN=============================
	
	def _create_version_file(self, filename):
		git_path = git_detect()
		f = open(filename, 'w+')
		os.chdir(self.SRC_DIR)
		print('>> Find git in PKG_DIR == {}'.format(self.SRC_DIR))
		_cmd = '\"{}\" rev-list --count HEAD'.format(git_path)
		print('>> _cmd', _cmd)
		try:
			repo_rev = os.popen(_cmd).read()[:8].rstrip()
		except Exception as _ex:
			print('<< Exception', _ex)
			repo_rev = ''
		os.chdir('../')
		print('<< repo_rev', repo_rev)
		repo_rev_rebuild = build_git_version(repo_rev)
		f.write('COMMIT_REVISION = "{}"\n\n'.format(repo_rev_rebuild))
		f.write('BUILD_TIME = {}\n\n'.format(time.time()))
		f.close()
		return repo_rev_rebuild
	
	# ======VERSION_END===============================
	# ================================================
	
	def build_release(self, sdist=False):
		
		print('>> Build stat files to working dir')
		self._build_manifest()
		self._build_config()
		
		print('>> Compiling py to cython')
		if self.buildcopy is False:
			if sdist:
				self._build_package_sdist()
			else:
				self._build_package()
		os.chdir(self.HERE)
	
	def build_instance(self):
		
		print('>> Copy dist app to release dir')
		self._copy_pkg_to_releasedir()
		
		print('>> Copy stat files to release dir')
		self._copy_instance_to_releasedir()
	
	def build_get(self, *_args, **_kwargs):
		self.build_release()
		self.build_instance()
		self.clean_build_dir()
	
	def install_last(self):
		print('>> Get Realese Last', self.LAST_REALESE_DIR)
		try:
			file_name = get_files_from_dir(self.LAST_REALESE_DIR)[0]
		except Exception as _ex:
			print('<< Exception', _ex)
			return
		print('>> Install Realese Last', file_name)
		try:
			os.chdir(self.LAST_REALESE_DIR)
			os.system(f'pip install {file_name} --no-deps --force-reinstall')
		except Exception as _ex:
			print('<< Exception', _ex)
