"""
Setup file for Self-Adaptive Cloud Infrastructure package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="self-adaptive-cloud",
    version="1.0.0",
    author="Cloud ML Engineering Team",
    author_email="support@example.com",
    description="Self-Adaptive Cloud Infrastructure with ML-Based Anomaly Detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/self-adaptive-cloud",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=6.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "matplotlib>=3.7.0",
        "boto3>=1.28.0",
        "azure-identity>=1.13.0",
        "google-cloud-compute>=1.13.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "aws": ["boto3>=1.28.0"],
        "azure": ["azure-identity>=1.13.0", "azure-compute>=30.0.0"],
        "gcp": ["google-cloud-compute>=1.13.0"],
    },
    entry_points={
        "console_scripts": [
            "self-adaptive-cloud=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
