from setuptools import setup

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
            'ntk = src.ntk:main',
        ],
    },
    python_requires='>=3.6',
)