from setuptools import setup

setup(
    name='homesens',
    packages=['homesens'],
    include_package_data=True,
    install_requires=[
        'homesens',
        'matplotlib',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
