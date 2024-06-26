import re
from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get version from __init__.py
def get_version():
    with open('uniclip/__init__.py', 'r') as f:
        content = f.read()
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", content)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="uniclip",
    version=get_version(),
    author="Cedar Ren",
    author_email="cedar.ren@gmail.com",
    description="A clipboard synchronization tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renxida/uniclip",
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi",
        "uvicorn",
        "waitress",
        "pydantic",
        "requests",
        "pyperclip",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "uniclip=uniclip.main:main",
        ],
    },
)
