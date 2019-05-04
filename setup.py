from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='smaker',
    version='0.0.1',
    author='Max Hoffman',
    author_email='max@factual.com',
    description='Generalize snakemake workflows',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['smaker'],
    install_requires=[
        ' datrie @ git+https://github.com/pytries/datrie.git',
        'click>=7.0',
        'backports.tempfile>=1.0',
        'snakemake>=5.4.5',
        'numpy>=1.14.2',
    ],
    entry_points={
        'console_scripts': ['smaker=snakerunner.cli:main']
    }
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
