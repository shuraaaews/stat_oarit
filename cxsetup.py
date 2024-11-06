from cx_Freeze import setup, Executable


executables = [Executable('stat_oarit.py',
                            base='WIN32GUI',
                            target_name = 'stat_oarit',
                            icon='stat_oarit_icon.ico')]

zip_include_packages = ['pillow', 'Babel', 'matplotlib',
                        'tkcalendar', 'ttkwidgets']

include_files = ['stat_oarit', 'stat_oarit/Data', 'stat_oarit/images']


options = {
    'build.exe': {
            'include_msvcr': True,
            'zip_include_packages' : zip_include_packages,
            'include_files' : include_files,
            }
    }

setup(
    name='stat_oarit',
    version='1.0',
    author='Evsunin A.',
    description="Data entry application for OARIT",
    packages=['stat_oarit'],
    executables=executables,
    options=options)
