from setuptools import setup

SETUP_INFO = dict(
    name='picsel',
    version='0.0.1',
    install_requires=['unipath', 'argh', 'six', 'python-dateutil'],
    scripts=['shotwell2blog.py', 'digikam2blog.py'],
    description="Export tagged photos from a Shotwell or DigiKam photo database",
    license='Free BSD',
    author='Luc Saffre',
    author_email='luc.saffre@gmail.com')

SETUP_INFO.update(classifiers="""\
Programming Language :: Python
Programming Language :: Python :: 3
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent""".splitlines())

SETUP_INFO.update(long_description=open("README.rst").read())

if __name__ == '__main__':
    setup(**SETUP_INFO)
