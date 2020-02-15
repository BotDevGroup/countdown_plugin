from distutils.core import setup
from setuptools import find_packages

REQUIREMENTS = [
    'marvinbot',
    'bs4'
]

setup(name='countdown_plugin',
      version='0.1',
      description='Plugin for search the series or movies countdown on yourcountdown.to',
      author='Conrado Reyes',
      author_email='coreyes@gmail.com',
      url='',
      packages=[
        'countdown_plugin',
      ],
      package_dir={
        'countdown_plugin':'countdown_plugin'
      },
      zip_safe=False,
      include_package_data=True,
      package_data={'': ['*.ini']},
      install_requires=REQUIREMENTS,
      dependency_links=[
          'git+ssh://git@github.com:BotDevGroup/marvin.git#egg=marvinbot',
      ],
)
