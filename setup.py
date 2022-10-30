from setuptools import setup

# python setup.py develop
setup(
    name='mkdocs-toc-md',
    version='0.0.1',
    description='Generate a toc markdown file',
    keywords='mkdocs toc',
    author='Ryo Tsunoda',
    author_email='try0.development@gmail.com',
    license='MIT',
    install_requires=[
        'mkdocs>=1.1',
        'beautifulsoup4>=4.6.3',
    ],
    python_requires='>=3.6',
    packages=['mkdocs_toc_md'],
    entry_points={
        'mkdocs.plugins': [
            'toc-md = mkdocs_toc_md.plugin:TocMdPlugin',
        ]
    },
)