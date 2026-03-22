from setuptools import setup, find_packages

setup(
    name="analog-voice-denoiser",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
    ],
    entry_points={
        "console_scripts": [
            "avd=denoiser:main",
        ],
    },
)
