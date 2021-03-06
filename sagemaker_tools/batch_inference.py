import argparse
import yaml
import boto3
from boto3.session import Session
from logging import getLogger, StreamHandler, INFO

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False

import sagemaker
from sagemaker.transformer import Transformer
from sagemaker.chainer.model import ChainerModel
from sagemaker.pytorch.model import PyTorchModel


def _model_exists(client, model_name):
    models = []
    res = client.list_models(MaxResults=10)
    models.extend([m['ModelName'] for m in res['Models']])
    while 'NextToken' in res:
        res = client.list_models(NextToken=res['NextToken'], MaxResults=10)
        models.extend([m['ModelName'] for m in res['Models']])
    models = set(models)
    return model_name in models

def batch_inference(session, client, model_name, setting, pytorch):
    sagemaker_session = sagemaker.Session(
        boto_session=session,
        sagemaker_client=client)

    conf = yaml.load(open(setting))

    # check the target model exists
    if _model_exists(client, model_name):
        logger.info('use the registered model.')
        deploy_args = conf['deploy']
        deploy_args['model_name'] = model_name
        deploy_args['base_transform_job_name'] = model_name
        deploy_args['sagemaker_session'] = sagemaker_session

        transformer = Transformer(**deploy_args)

    else:
        # [TODO] updateing case (delete and create).
        # Basically, models have dependencies on multiple endpoints and inference jobs,
        # so it is not easy to delete it.
        logger.info('register the new model.')
        model_args = conf['model']
        model_args['sagemaker_session'] = sagemaker_session
        model_args['name'] = model_name
        if pytorch:
            model = PyTorchModel(**model_args)
        else:
            model = ChainerModel(**model_args)

        deploy_args = conf['deploy']
        transformer = model.transformer(**deploy_args)  # register model

    transform_args = conf['transform']
    # use default job_name (model_name + datetime.now())
    transformer.transform(**transform_args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name', type=str,
                        help='Model name.')
    parser.add_argument('setting', type=str,
                        help='Path to setting file.')
    parser.add_argument('--profile_name', '-p', type=str, default=None,
                        help='When execute a training from local, enter the profile name.')
    parser.add_argument('--pytorch', '-t', action='store_true')
    args = parser.parse_args()

    if args.profile_name is None:
        session = Session()
        client = boto3.client('sagemaker', region_name=session.region_name)
    else:
        session = Session(profile_name=args.profile_name)
        credentials = session.get_credentials()

        client = boto3.client('sagemaker', region_name=session.region_name,
                              aws_access_key_id=credentials.access_key,
                              aws_secret_access_key=credentials.secret_key,
                              aws_session_token=credentials.token)

    batch_inference(session, client, args.model_name, args.setting, args.pytorch)