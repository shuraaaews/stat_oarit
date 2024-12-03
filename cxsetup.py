from cx_Freeze import setup, Executable

target_name = 'stat_oarit'

shortcut_data = [
  # (Type, Folder, Name, ?, Target exe, arguments, description, hotkey, icon, icon index, show cmd, Working dir)
  (
    'DesktopShortcut', 'DesktopFolder', 'stat_oarit', 'TARGETDIR',
    '[TARGETDIR]' + target_name, None,
    'Data entry application for OARIT', None,
    None, None, None, 'TARGETDIR'
  )]
executables = [Executable('stat_oarit.py',
                            base='WIN32GUI',
                            target_name = target_name,
                            icon='stat_oarit_icon.ico')]

addtional_mods = ['numpy.core._methods', 'numpy.lib.format']
packages = ['numpy', 'pillow', 'Babel', 'matplotlib', 'tkcalendar', 'ttkwidgets']

include_files = ['stat_oarit', 'stat_oarit/Data', 'stat_oarit/images']


options = {
    'build.exe': {
	'packages' : packages,            
	'include_msvcr': True,
	'includes' : addtional_mods,
	'include_files' : include_files,
            },
    'bdist_msi': {
      'data': {'Shortcut': shortcut_data}
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
