from setuptools import setup, find_packages

setup(
    name='xyz',
    version='0.3',
    author='BlackSheep Netmind.AI',
    author_email='xiangpeng.wan@protagolabs.com',
    packages=find_packages(),
    install_requires=[
        'openai',
        'langchain',
        'openpyxl',
        'networkx',
        'pymilvus',
        'pymongo',
        'pytest',
    ],
    # commandline-app 
    # entry_points={
    #     'console_scripts': [
    #         'memory=memory_scripts.script:main',
    #     ],
    # },
    description='A package which can help user to using memory tool to create and search memory',
)
