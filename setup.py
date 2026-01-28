from setuptools import setup, find_packages

setup(
    name="wiki_scraper",
    version="0.1.0",
    author="Michał Pilarski",
    description="A Python package for scraping and analyzing wiki pages",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires='>=3.14',
    install_requires=open("requirements.txt").read().split(),
)