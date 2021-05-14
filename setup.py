from setuptools import setup

tests_require = [
    "flake8==3.9.2",
    "nose==1.3.7"
]

setup(
    name='next-theme-kit',
    author="29next",
    author_email="dev@29next.com",
    version='0.1',
    install_requires=[
        "PyYAML==5.4.1",
        "requests==2.25.1",
        "watchgod==0.7"
    ],
    entry_points={
        'console_scripts': [
            'ntk = ntk:main',
        ],
    },
    package_dir={'': 'src'},
    python_requires='>=3.6',
    test_suite='nose.collector',
    tests_require=tests_require,
    extras_require={
        'test': tests_require
    },
)
