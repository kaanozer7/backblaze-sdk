from setuptools import setup, find_packages

setup(
    name="backblaze_sdk",
    version="0.1.0",
    author="Kaan Ozer",
    author_email="kaanozer7@gmail.com",
    description="Backblaze B2 SDK for uploading, downloading, and managing videos and json files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kaanozer7/backblaze-sdk",
    packages=find_packages(),
    install_requires=[
        "b2sdk",
        "requests",
        "python-dotenv"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
