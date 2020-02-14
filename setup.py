# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sage_extensions', 'sagemaker_tools', 'smtools', 'smtools.extensions']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.11.0,<2.0.0',
 'chainer==6.0.0',
 'colorama>=0.4.3,<0.5.0',
 'joblib>=0.14.1,<0.15.0',
 'matplotlib>=3.1.2,<4.0.0',
 'numpy>=1.18.1,<2.0.0',
 'pandas>=0.25.3,<0.26.0',
 'pillow>=6.2.1,<7.0.0',
 'pyyaml>=5.3,<6.0',
 'sagemaker>=1.50.1,<2.0.0',
 'slackweb>=1.0.5,<2.0.0',
 'tqdm>=4.41.1,<5.0.0']

entry_points = \
{'console_scripts': ['mgconf = smtools.merge_configs:main',
                     'smbatch = sagemaker_tools.batch_inference:main',
                     'smdeploy = sagemaker_tools.deploy_endpoint:main',
                     'smtrain = sagemaker_tools.exec_train:main']}

setup_kwargs = {
    'name': 'smtools',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'hrsma2i',
    'author_email': 'hrs.ma2i@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
