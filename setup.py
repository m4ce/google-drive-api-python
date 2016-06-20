from distutils.core import setup

version = '0.0.4'

setup(
  name = 'google-drive-api',
  packages = ['google_drive'],
  version = version,
  description = 'Python library for Google Drive API',
  author = 'Matteo Cerutti',
  author_email = 'matteo.cerutti@hotmail.co.uk',
  url = 'https://github.com/m4ce/google-drive-api-python',
  download_url = 'https://github.com/m4ce/google-drive-api-python/tarball/%s' % (version,),
  keywords = ['google', 'drive', 'google drive'],
  classifiers = [],
  install_requires = ["google-api-python-client"]
)
