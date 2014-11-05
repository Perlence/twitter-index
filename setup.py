from setuptools import setup, find_packages

setup(
    name='twitter-index',
    description='Index home feed and favorite tweets.',
    version='0.1.0',
    author='Sviatoslav Abakumov',
    author_email='dust.harvesting@gmail.com',
    url='https://bitbucket.org/Perlence/twitter-index',
    platforms=['MacOS X', 'Unix', 'POSIX'],
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'arrow',
        'gevent',
        'logbook',
        'schedule',
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
