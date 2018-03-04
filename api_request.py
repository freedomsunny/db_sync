import requests


def get_http(url='/', data='', method='get', headers={}, files=''):
    request = getattr(requests, method)
    return request(url, data=data, headers=headers, files=files, verify=False)


def post_http(url='/', data='', method='post', headers={}, files=''):
    post = getattr(requests, method)
    return post(url, data=data, headers=headers, files=files, verify=False)

