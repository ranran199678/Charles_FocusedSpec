#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Charles_FocusedSpec - Setup
מערכת חיזוי מניות פורצות - קובץ התקנה

קובץ זה מגדיר את התקנת המערכת באמצעות pip
"""

from setuptools import setup, find_packages
import os

# קריאת תוכן README
def read_readme():
    """קורא את קובץ README"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Charles_FocusedSpec - מערכת חיזוי מניות פורצות"

# קריאת דרישות
def read_requirements():
    """קורא את קובץ requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="charles-focused-spec",
    version="1.0.0",
    author="Charles_FocusedSpec Team",
    author_email="team@charles-focused-spec.com",
    description="מערכת חיזוי מניות פורצות מתקדמת",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/charles-focused-spec/charles-focused-spec",
    project_urls={
        "Bug Tracker": "https://github.com/charles-focused-spec/charles-focused-spec/issues",
        "Documentation": "https://charles-focused-spec.readthedocs.io/",
        "Source Code": "https://github.com/charles-focused-spec/charles-focused-spec",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=8.3.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "dashboard": [
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
            "altair>=5.0.0",
        ],
        "ml": [
            "torch>=1.13.0",
            "tensorflow>=2.10.0",
            "scikit-learn>=1.0.0",
            "transformers>=4.46.0",
        ],
        "full": [
            "charles-focused-spec[dashboard,ml,dev]",
        ],
    },
    entry_points={
        "console_scripts": [
            "charles-focused-spec=main:main",
            "cfs=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"],
    },
    keywords=[
        "trading",
        "stock-analysis",
        "technical-analysis",
        "machine-learning",
        "artificial-intelligence",
        "financial-analysis",
        "investment",
        "trading-signals",
        "stock-prediction",
        "market-analysis",
    ],
    license="MIT",
    platforms=["any"],
    zip_safe=False,
) 