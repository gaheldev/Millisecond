pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'millisecond'
gnome = import('gnome')

gnome.compile_resources('millisecond',
  'millisecond.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'millisecond.in',
  output: 'millisecond',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

millisecond_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'diagnostic.py',
  'rtcqs.py',
]

install_subdir(
  'rtfix',
  install_dir: moduledir
)

install_data(millisecond_sources, install_dir: moduledir)
