"""
Fyle Jobs
"""
from typing import Dict

from fylesdk import FyleSDK


class FyleJobsSDK:
    """
    Fyle Jobs SDK
    """

    def __init__(self, jobs_url: str, fyle_sdk_connection: FyleSDK):
        self.user_profile = fyle_sdk_connection.Employees.get_my_profile()['data']
        self.jobs_url = jobs_url
        self.access_token = fyle_sdk_connection.access_token
        self.fyle_sdk_connection = fyle_sdk_connection

    def trigger_now(self, callback_url: str, callback_method: str,
                    job_description: str, object_id: str, payload: any = None,
                    job_data_url: str = None) -> Dict:
        """
        Trigger callback immediately
        :param payload: callback payload
        :param callback_url: callback URL for the job
        :param callback_method: HTTP method for callback
        :param job_description: Job description
        :param job_data_url: Job data url
        :param object_id: object id
        :returns: response
        """
        body = {
            'template': {
                'name': 'http.main',
                'data': {
                    'url': callback_url,
                    'method': callback_method,
                    'payload': payload
                }
            },
            'job_data': {
                'description': job_description,
                'url': '' if not job_data_url else job_data_url
            },
            'job_meta_data': {
                'object_id': object_id
            },
            'notification': {
                'enabled': False
            },
            'org_user_id': self.user_profile['id']
        }

        response = self.fyle_sdk_connection.Jobs.trigger_now(
            callback_url=callback_url,
            callback_method=callback_method, object_id=object_id, payload=body,
            job_description=job_description,
            org_user_id=self.user_profile['id']
        )

        return response

    def trigger_interval(self, callback_url: str, callback_method: str,
                         job_description: str, object_id: str, hours: int,
                         start_datetime: str, job_data_url: str = None) -> Dict:
        """
        Trigger callback on Interval
        :param start_datetime: start datetime for job
        :param hours: repeat in hours
        :param callback_url: callback URL for the job
        :param callback_method: HTTP method for callback
        :param job_description: Job description
        :param job_data_url: Job data url
        :param object_id: object id
        :returns: response
        """
        body = {
            'template': {
                'name': 'http.main',
                'data': {
                    'url': callback_url,
                    'method': callback_method
                }
            },
            'job_data': {
                'description': job_description,
                'url': '' if not job_data_url else job_data_url
            },
            'job_meta_data': {
                'object_id': object_id
            },
            'trigger': {
                'type': 'interval',
                'when': {
                    'hours': hours,
                    'start_date': start_datetime
                }
            },
            'notification': {
                'enabled': False
            },
            'org_user_id': self.user_profile['id']
        }

        response = self.fyle_sdk_connection.Jobs.trigger_interval(
            callback_url=callback_url,
            callback_method=callback_method, object_id=object_id, payload=body,
            job_description=job_description,
            org_user_id=self.user_profile['id'],
            start_datetime=start_datetime,
            hours=hours
        )

        return response

    def delete_job(self, job_id):
        """
        Delete job
        :param job_id: id of the job to delete
        :return:
        """

        response = self.fyle_sdk_connection.Jobs.delete_job_request(job_id)
        return response
