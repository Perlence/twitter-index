from setuptools import setup, find_packages

setup(
    name='twitter-index',
    description='Index your home timeline and favorited tweets.',
    version='0.1',
    author='Sviatoslav Abakumov, Anastasiya Kozayeva',
    author_email='dust.harvesting@gmail.com',
    url='https://github.com/Perlence/twitter-index',
    platforms=['MacOS X', 'Unix', 'POSIX'],
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'tiworker = twitterindex.worker:main',
            'startapp = twitterindex.app:start',
            'debugapp = twitterindex.app:debug',
        ],
    },
    install_requires=[
        'arrow',
        'Flask',
        'Flask-Assets',
        'gevent',
        'logbook',
        'termcolor',
        'twitter',
        'Whoosh',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
