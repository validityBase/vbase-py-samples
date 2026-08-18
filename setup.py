"""vBase Python Software Development Kit (SDK) Samples."""

from pathlib import Path

from setuptools import find_packages, setup

ROOT_DIR = Path(__file__).resolve().parent
long_description = (ROOT_DIR / "README.md").read_text(encoding="utf-8")

requirements = []
for raw_line in (ROOT_DIR / "requirements/base.in").read_text(
    encoding="utf-8"
).splitlines():
    line = raw_line.split("#", 1)[0].strip()
    if line and not line.startswith("-"):
        requirements.append(line)

setup(
    name="vbase_samples",
    version="0.0.1",
    author="PIT Labs, Inc.",
    author_email="tech@vbase.com",
    description="vBase Python Software Development Kit (SDK) Samples",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/validityBase/vbase-py-samples",
    packages=find_packages(),
    package_data={
        "": ["../requirements/base.in"],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
