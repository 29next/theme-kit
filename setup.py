from setuptools import setup, find_packages

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
    test_suite="tests.test_suite",
    python_requires='>=3.6',
    tests_require=[
        "flake8==3.9.2",
    ],
)
