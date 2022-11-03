from asyncio.log import logger
from unittest import mock
from rest_framework.response import Response
from rest_framework.views import status
from apps.fyle.helpers import *


def test_post_request(mocker):
    mocker.patch(
        'apps.fyle.helpers.requests.post',
        return_value=Response(
            {
                'message': 'Post request'
            },
            status=status.HTTP_200_OK
        )
    )
    try:
        post_request(url='sdfghjk', body={}, refresh_token='srtyu')
    except:
        logger.info('Error in post request')
    
    mocker.patch(
        'apps.fyle.helpers.requests.post',
        return_value=Response(
            {
                'message': 'Post request'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    )
    try:
        post_request(url='sdfghjk', body={}, refresh_token='srtyu')
    except:
        logger.info('Error in post request')


def test_get_request(mocker):
    mocker.patch(
        'apps.fyle.helpers.requests.get',
        return_value=Response(
            {
                'message': 'Get request'
            },
            status=status.HTTP_200_OK
        )
    )
    try:
        get_request(url='sdfghjk', params={'sample': True}, refresh_token='srtyu')
    except:
        logger.info('Error in post request')

    mocker.patch(
        'apps.fyle.helpers.requests.get',
        return_value=Response(
            {
                'message': 'Get request'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    )
    try:
        get_request(url='sdfghjk', params={'sample': True}, refresh_token='srtyu')
    except:
        logger.info('Error in post request')


def test_get_cluster_domain(mocker):
    mocker.patch(
        'apps.fyle.helpers.requests.post',
        return_value=Response(
            {
                'message': 'Post request'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    )
    try:
        get_cluster_domain(refresh_token='srtyu')
    except:
        logger.info('Error in post request')
