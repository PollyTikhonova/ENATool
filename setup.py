"""
Setup script for ENATool package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='ENATool',
    version='2.0.0',
    
    # Package info
    description='Comprehensive tool for downloading and managing ENA sequencing data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    # Author info
    author='P.Tikhonova',
    author_email='tikhonova.polly@mail.ru',
    
    # URLs
    url='https://github.com/PollyTikhonova/ENATool',
    project_urls={
        'Bug Reports': 'https://github.com/PollyTikhonova/ENATool/issues',
        'Source': 'https://github.com/PollyTikhonova/ENATool',
        'Documentation': 'https://github.com/PollyTikhonova/ENATool#readme',
    },
    
    # License
    license='MIT',
    
    # Packages
    packages=find_packages(),
    
    # Include additional files
    package_data={
        'ENATool': ['*.md'],
    },
    include_package_data=True,
    
    # Python version requirement
    python_requires='>=3.7',
    
    # Dependencies
    install_requires=[
        'pandas>=0.23.4',
        'requests>=2.20.0',
        'tqdm>=4.0.0',
        'numpy>=1.15.0',
        'xmltodict>=0.12.0',
        'lxml>=4.0.0'
    ],
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
            'black>=21.0',
            'flake8>=3.9',
        ]
    },
    
    # Classification
    classifiers=[      
        # Intended audience
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        
        # Topic
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        
        # License
        'License :: OSI Approved :: MIT License',
        
        # Python versions
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        
        # OS
        'Operating System :: OS Independent',
        
        # Other
        'Natural Language :: English',
    ],
    
    # Keywords
    keywords='bioinformatics sequencing ENA FASTQ download metadata genomics',
    
    # Entry points for command-line scripts
    entry_points={
        'console_scripts': [
            'enatool=ENATool.cli:main',
        ],
    },
    
    # Project maturity
    zip_safe=False,
)
