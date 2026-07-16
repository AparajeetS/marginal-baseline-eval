from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as handle:
    long_description = handle.read()


setup(
    name="mbe-eval",
    version="0.3.2",
    author="Aparajeet Shadangi",
    author_email="aparajeet.shadangi@proton.me",
    description="Marginal Baseline Evaluation for auditing machine-learning training metrics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AparajeetS/marginal-baseline-eval",
    project_urls={
        "Source": "https://github.com/AparajeetS/marginal-baseline-eval",
        "Issues": "https://github.com/AparajeetS/marginal-baseline-eval/issues",
        "Documentation": "https://github.com/AparajeetS/marginal-baseline-eval/blob/master/docs/README.md",
        "Evidence": "https://github.com/AparajeetS/marginal-baseline-eval/blob/master/SUPPORTING_EVIDENCE.md",
        "Research Program": "https://github.com/AparajeetS/marginal-baseline-eval/blob/master/docs/MBE_2_RESEARCH_PROGRAM.md",
        "Replication Protocol": "https://github.com/AparajeetS/marginal-baseline-eval/blob/master/docs/INDEPENDENT_REPLICATION_PROTOCOL.md",
        "Kaggle Notebook": "https://www.kaggle.com/code/aparajeetshadangi/audit-ml-training-metrics-with-mbe",
    },
    packages=find_packages(exclude=["experiments*", "examples*", "docs*", "tests*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords=[
        "machine learning",
        "metrics",
        "evaluation",
        "generalization",
        "partial correlation",
        "reproducibility",
    ],
    license="MIT",
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24",
        "pandas>=2.0",
        "scipy>=1.10",
    ],
    extras_require={
        "torch": ["torch>=2.0", "torchvision>=0.15"],
        "checkpoint": ["h5py>=3.10"],
        "flexible": ["scikit-learn>=1.3"],
        "plot": ["matplotlib>=3.7", "seaborn>=0.12"],
        "examples": ["torch>=2.0", "torchvision>=0.15", "scikit-learn>=1.3"],
        "dev": ["pytest>=7", "build>=1.0", "twine>=4"],
    },
    entry_points={
        "console_scripts": [
            "mbe-eval-audit=mbe_eval.cli:main",
            "mbe-eval-demo=mbe_eval.demo:main",
        ]
    },
)
