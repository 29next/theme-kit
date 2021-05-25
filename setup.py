from setuptools import setup

__version__ = '0.0.4'

tests_require = [
    "flake8==3.9.2",
    "nose==1.3.7"
]

with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='next-theme-kit',
    author="29next",
    author_email="dev@29next.com",
    url='https://github.com/29next/theme-kit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=__version__,
    install_requires=[
        "PyYAML>=5.4",
        "requests>=2.25",
        "watchgod>=0.7"
    ],
    entry_points={
        'console_scripts': [
            'ntk = ntk:main',
        ],
    },
    package_dir={'': 'src'},
    python_requires='>=3.6'
)
