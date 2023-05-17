from setuptools import setup

setup(
    name="flake8_platform_checks",
    version='0.1.0',
    install_requires=[
        "setuptools",
        "flake8 > 5.0.0",
    ],
    entry_points={
        'flake8.extension': [
            'PRI = restrict_imports:Plugin',
            'ETA = enforce_type_annotations:Plugin',
            'EKO = enforce_kwargs_only:Plugin'
        ],
    },
)