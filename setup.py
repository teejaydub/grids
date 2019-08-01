from setuptools import setup

setup(
    name='grids',
    version='0.1',
    py_modules=['grids'],
    install_requires=[
        'Click', 'pyyaml'
    ],
    entry_points='''
        [console_scripts]
        grids=grids:cli
    ''',
)
