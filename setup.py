from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="genai-platform",
    version="0.1.0",
    author="GenAI Platform Team",
    description="Production-ready, cloud-agnostic Generative AI platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VenkataAnilKumar/GenerativeAIProjects",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "openai>=1.10.0",
        "langchain>=0.1.6",
    ],
)
