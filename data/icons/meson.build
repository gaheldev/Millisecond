application_id = 'io.github.gaheldev.Millisecond'

scalable_dir = 'hicolor' / 'scalable' / 'apps'
install_data(
  scalable_dir / ('@0@.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
install_data(
  symbolic_dir / ('@0@-symbolic.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)

install_data(
  'scalable/actions/external-link-symbolic.svg',
  'scalable/actions/info-outline-symbolic.svg',
  'scalable/actions/emblem-important-symbolic.svg',
  'scalable/actions/selection-mode-symbolic.svg',
  'scalable/actions/dialog-warning-symbolic.svg',
  'scalable/actions/view-refresh-symbolic.svg',
  install_dir: get_option('datadir') / 'icons/hicolor/scalable/actions'
)
