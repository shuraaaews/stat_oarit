#setup.py
from setuptools import setup


setup(
    name='stat_oarit',
    version='1.0',
    author='Evsunin A.',
    description= "Data entry application for OARIT",
    packages=[
        'stat_oarit',
        'stat_oarit.Data',
        'stat_oarit.images'
    ],
    install_requires=[
      'Babel', 'matplotlib', 'pillow', 'tkcalendar', 'ttkwidgets'],
    
    python_requires='>=3.6',
    package_data={'stat_oarit.Data': ['*.csv'],
                    'stat_oarit.images': ['*.png', '*.xbm']},
    entry_points={
        'console_scripts': [
          'stat_oarit = stat_oarit.__main__:main']
            }
    )
