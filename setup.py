from setuptools import find_packages, setup

setup(
    name="myturn_bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Click",
        "requests",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "myturn_bot = myturn_bot.cli:cli",
        ],
    },
    python_requires=">=3.10.0",
)
