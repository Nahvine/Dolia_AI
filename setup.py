from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="doliaai",
    version="1.0.0",
    author="Nahvine",
    author_email="enderboyvn81@gmail.com",
    description="An intelligent computer control system using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nahvine/DoliaAI",
    project_urls={
        "Bug Tracker": "https://github.com/Nahvine/DoliaAI/issues",
        "Documentation": "https://github.com/Nahvine/DoliaAI#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "doliaai=main:main",
        ],
    },
) 