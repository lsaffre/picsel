from setuptools import setup

SETUP_INFO = dict(
    name='shotwell2blog',
    version='0.0.1',
    install_requires=['argh'],
    scripts=['shotwell2blog.py'],
    description="Export tagged photos and videos from Shotwell photo database",
    license='Free BSD',
    author='Luc Saffre',
    author_email='luc.saffre@gmail.com')

SETUP_INFO.update(classifiers="""\
Programming Language :: Python
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent""".splitlines())

SETUP_INFO.update(long_description=open("README.rst").read())

if __name__ == '__main__':
    setup(**SETUP_INFO)
