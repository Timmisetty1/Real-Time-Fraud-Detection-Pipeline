"""
Setup script for fraud detection pipeline
"""
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='fraud-detection-pipeline',
    version='1.0.0',
    description='Real-time fraud detection pipeline using machine learning',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Timmisetty',
    url='https://github.com/Timmisetty1/Real-Time-Fraud-Detection-Pipeline',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    entry_points={
        'console_scripts': [
            'fraud-pipeline=pipeline:main',
            'fraud-api=api:main',
            'fraud-generator=generate_transactions:main',
        ],
    },
)
