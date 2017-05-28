from setuptools import find_packages, setup

import pyflash


dependencies = open('requirements.txt').read().splitlines()

description = 'Get flash like superpowers by automating everyday tasks!'
with open('README.rst') as fh:
    long_description = fh.read()


setup(
    name='pyflash',
    version=pyflash.__version__,
    url='https://github.com/chillaranand/pyflash',
    license='BSD',
    author='Chillar Anand',
    author_email='anand21nanda@gmail.com',
    description=description,
    long_description=long_description,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,

    entry_points={
        'console_scripts': [
            'flash = pyflash.cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',

        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',

        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',

        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
