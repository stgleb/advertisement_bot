from setuptools import find_packages
from setuptools import setup

setup(
    name='advertisement-bot',
    version='1.0',
    description='Advertisement bot',
    long_description="""Advertisement bot""",
    author='Gleb Stepanov',
    author_email='glebstepanov1992@gmail.com',
    install_requires=['PyYAML==3.10', "argparse==1.2.1","requests==2.2.1","beautifulsoup4==4.3.2"],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'adv-up = adv_bot.adv_up:main',
        ],
    }
)