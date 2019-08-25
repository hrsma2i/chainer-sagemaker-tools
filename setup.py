from setuptools import setup, find_packages


with open("requirements.txt") as requirements_file:
    install_requires = requirements_file.read().splitlines()

setup(
    author="tn1031",
    author_email="ttt.nakamura1031@gmail.com",
    name="smtools",
    description="Some extensions and tools to run Chainer jobs on Amazon SageMaker",
    version="0.1.8.4",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "smtrain=sagemaker_tools.exec_train:main",
            "smdeploy=sagemaker_tools.deploy_endpoint:main",
            "smbatch=sagemaker_tools.batch_inference:main",
            "mgconf=smtools.merge_configs:main",
        ]
    },
    license="MIT license",
)
