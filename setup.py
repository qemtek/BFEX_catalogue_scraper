import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bfx-market-catalogue-scraper", # Replace with your own username
    version="0.0.1",
    author="Christopher Collins",
    author_email="qemtek@gmail.com",
    description="A package for downloading market catalogue information from the Betfair Exchange API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)