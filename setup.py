from setuptools import setup, find_packages

setup(
    name="nos-ai-project",
    version="4.19.2",
    packages=find_packages(),
    python_requires=">=3.10",
    extras_require={"m1-learning": ["torch>=2.0"]},
)
