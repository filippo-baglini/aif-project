from setuptools import setup, find_packages

# Helper function to parse requirements.txt
def parse_requirements(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

setup(
    name="aif_project",
    version="0.1.0",
    author="Nico Conti",
    description="Aif course project for Master degree at Pisa University",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,  # Include non-Python files
    package_data={
        "aif_project": ["results/*.txt"],  # Specify the .txt files to include
    },
    install_requires=parse_requirements("requirements.txt"),  # Automatically read requirements
)
