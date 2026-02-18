from setuptools import setup, find_packages

setup(
    name="databricks-dbt-framework",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "dbt-core>=1.0.0",
        "dbt-databricks>=1.0.0",
        "requests>=2.25.0",
        "pyodbc>=4.0.0",
        "jaydebeapi>=1.2.0",
        "PyYAML>=5.4.0"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A metadata-driven DBT framework for Databricks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/databricks-dbt-framework",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)