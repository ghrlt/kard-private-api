import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="kard-private-api",
    version="2.1",
    author="Gaëtan Hrlt",
    author_email="gaetan.hrlt+dev@gmail.com",
    description="Control and Automate your Kard account",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ghrlt/kard-private-api",
    project_urls={
    	"Developer website": "https://ghr.lt?f=kard-private-api",
        "Bug Tracker": "https://github.com/ghrlt/kard-private-api/issues",
    },
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=["kard_private_api"],
    python_requires=">=3.6",
)