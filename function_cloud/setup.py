from setuptools import setup, find_packages

# Simple setup file compatible with older setuptools
setup(
    name="function-cloud",
    version="0.1.0",
    author="Saad Momin",
    author_email="saadmomin2903@example.com",
    description="Deploy Python functions to Modal.com with ease",
    url="https://github.com/Saadmomin2903/function-cloud",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "modal>=0.50.0",
    ],
    entry_points={
        "console_scripts": [
            "function-cloud=function_cloud.cli:main",
        ],
    },
    extras_require={
        "llm": ["groq>=0.4.0"],
        "auth": [
            "requests>=2.25.0",
            "oauthlib>=3.1.0",
        ],
        "web": [
            "flask>=2.0.0",
            "flask-login>=0.6.0",
            "requests>=2.25.0",
            "oauthlib>=3.1.0",
        ],
        "all": [
            "groq>=0.4.0",
            "flask>=2.0.0",
            "flask-login>=0.6.0",
            "requests>=2.25.0",
            "oauthlib>=3.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.950",
        ],
    },
)
