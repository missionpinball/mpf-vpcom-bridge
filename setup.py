#!/usr/bin/env python

from setuptools import setup, find_packages

DEPENDENCIES = ["mpf"]

setup(
	name="mpf_vpcom_bridge",
	version="0.1.1",
	author="The Mission Pinball Framework Team",
	author_email="brian@missionpinball.com",
	packages=['mpf_vpcom_bridge'],
	entry_points={
			"console_scripts": 
				["mpf_vpcom_bridge=mpf_vpcom_bridge.main:main"]
			},
	install_requires=DEPENDENCIES,
	python_requires=">=3.9",
	classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Topic :: Artistic Software',
        'Topic :: Games/Entertainment :: Arcade'

    ],
    keywords=["pinball"]
	)