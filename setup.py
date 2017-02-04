from setuptools import setup, find_packages

setup(
    name='sshsocksvpn',
    version='0.1',
    description='Simple badvpn-tun2socks wrapper',
    url='https://github.com/grimpy/sshsocksvpn',
    author='Jo De Boeck',
    author_email='deboeck.jo@gmail.com',
    license='GPLv2',
    classsifiers=[
        'Development Stats :: 4 - Beta',
        'Prgamming Language :: Python :: 3'
    ],
    packages=find_packages(exclude=['examples']),
    install_requires=['psutil'],
    entry_points={
        'console_scripts': ['sshsocksvpn=sshsocksvpn.__main__:main']
    }

)
