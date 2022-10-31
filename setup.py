import io
from setuptools import setup

# python setup.py develop
setup(
    name='mkdocs-toc-md',
    version='0.0.1',
    description='Generate a toc markdown file',
    long_description=io.open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    keywords='mkdocs plugin toc',
    author='Ryo Tsunoda',
    author_email='try0.development@gmail.com',
    url='https://github.com/try0/mkdocs-toc-md',
    license='MIT',
    install_requires=[
        'mkdocs>=1.1',
        'beautifulsoup4>=4.6.3',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation'
    ],
    python_requires='>=3.6',
    packages=['mkdocs_toc_md'],
    entry_points={
        'mkdocs.plugins': [
            'toc-md = mkdocs_toc_md.plugin:TocMdPlugin',
        ]
    },
)