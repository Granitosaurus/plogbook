from setuptools import setup


setup(
    name='plogbook',
    version='0.21',
    packages=['plogbook', 'plogbook.tests', 'plogbook.default_styles'],
    url='',
    license='see LICENSE',
    author='granitas',
    author_email='bernardas.alisauskas@gmail.com',
    package_data={'': ['/default_styles/*']},
    include_package_data=True,
    description='Plogbook is a console application for personal logging. It turns personal logs written in console or '
                'favorite text editor into readable html pages. The personal logs(plogs for short) are located in '
                'categories which are part of the plogbook'
)
