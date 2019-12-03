from setuptools import setup

with open('Readme.md') as f:
    readme = f.read()


setup(
    name='elodie',
    version='1.0.0',
    description='Your Personal EXIF-based Photo, Video and Audio Assistant',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Jaisen Mathai',
    author_email='jaisen@jmathai.com',
    url='https://github.com/jmathai/elodie',
    packages=[
        'elodie',
    ],
    entry_points={
        'console_scripts': [
            'elodie = elodie.elodie:main',
        ],
    },
    package_dir={'elodie': 'elodie'},
    include_package_data=True,
    install_requires=[
        'click==6.6',
        'requests==2.20.0',
        'Send2Trash==1.3.0',
        'future==0.16.0',
        'configparser==3.5.0',
        'tabulate==0.7.7',
        'Pillow==5.3.0',
    ],
    license="Apache 2.0",  # Not sure if this is correct
    keywords="photo organization photography",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
)

