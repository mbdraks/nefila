from setuptools import setup, find_packages

setup(
    name="nefila", 
    packages=find_packages(),
    version = '0.0.1',
    license='GPL-v3',
    description = 'Nefila is an elegant and simple Fortinet Security Fabric library for Python.',
    author = 'Michel Barbosa',
    author_email = 'nothing@nodomain.com',
    url = 'https://github.com/barbosm/nefila',
    download_url = 'https://github.com/barbosm/nefila/archive/v0.0.1.tar.gz',
    keywords = ['fortinet', 'fortigate', 'security fabric'],
    install_requires=[
        'requests',
    ],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GPL-v3 License',
    'Programming Language :: Python :: 3.7',
    ],
)
