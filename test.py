from src import main

def build(pkg_name='pkgbuilder', cmd=''):
	main.build_package(pkg_name, rf'reqs release packlasts {cmd} packages_path=d:\python\packages')


if __name__ == '__main__':
	build(cmd='install')
