# -*- coding: utf-8 -*-
import requests
import os
import sys

import pprint

sys.path.append(os.getcwd())
import properties

api_url = "https://api.sparkworks.net"
sso_url = "https://sso.sparkworks.net/aa/oauth/token"
client_id = properties.client_id
client_secret = properties.client_secret
token = {}

usernm = ""
passwd = ""

the_sites = []
the_site_resources = {}


def connect(username, password):
    global token, usernm, passwd
    token = getToken(username, password)
    usernm = username
    passwd = password


def getToken(username, password):
    global client_id, client_secret
    params = {'username': username, 'password': password, 'grant_type': "password", 'client_id': client_id,
              'client_secret': client_secret}
    response = requests.post(sso_url, params)
    return response.json()


def sites():
    global token, the_sites
    response = apiGetAuthorized('/v1/location/site')
    the_sites = response.json()["sites"]
    for site in the_sites:
        isReuse = False
        for user in site['sharedUsers']:
            if user['username'] == usernm and user['reusePermission']:
                    isReuse = True
        if isReuse:
            for subsite in site['subsites']:
                    the_sites.append(subsite)
    return the_sites


def main_site():
    for site in sites():
        if len(site["subsites"]) != 0:
            for user in site['sharedUsers']:
                if usernm == user['username'] and user['viewPermission'] and user['reusePermission']:
                    return site


def rooms():
    _rooms = []
    for site in sites():
        if len(site["subsites"]) != 0:
            pass
        else:
            _rooms.append(site)
    return _rooms


def select_rooms(room_names):
    _rooms = []
    for room_name in room_names:
        for site in sites():
            if site["name"].encode('utf-8') in room_name:
                _rooms.append(site)
                break
    return _rooms


def siteResources(site):
    if site["id"] not in the_site_resources:
        response = apiGetAuthorized("/v1/location/site/" + str(site["id"]) + "/resource")
        the_site_resources[site["id"]] = response.json()["resources"]
    return the_site_resources[site["id"]]


def siteResource(site, observedProperty):
    _resources = siteResources(site)
    for _resource in _resources:
        if _resource["uri"].startswith("site-") and _resource["property"] == observedProperty:
            return _resource


def siteResourceDevice(site, observedProperty):
    _resources = siteResources(site)
    for _resource in _resources:
        if (_resource["uri"].startswith("si") is not 1)  and _resource["property"] == observedProperty:
            return _resource


def siteResources_all(site, observedProperty):
    _selected_resources = []
    _resources = siteResources(site)
    for _resource in _resources:
        if observedProperty in _resource["property"]:
            _selected_resources.append(_resource)
    return _selected_resources


def siteResources_all_exact(site, observedProperty):
    _selected_resources = []
    _resources = siteResources(site)
    for _resource in _resources:
        if observedProperty == _resource["property"]:
            _selected_resources.append(_resource)
    return _selected_resources


def power_phases(site):
    _phases = {}
    _uris = []

    _resources = siteResources_all(site, "Calculated Power Consumption")
    for _resource in _resources:
        if not _resource["uri"].startswith("site-"):
            _phases[_resource["uri"]] = _resource
            _uris.append(_resource["uri"])
    _phases_ret = []
    for uri in sorted(_uris):
        _phases_ret.append(_phases[uri])
    return _phases_ret


def current_phases(site):
    _phases = {}
    _uris = []

    _resources = siteResources_all_exact(site, "Electrical Current")
    for _resource in _resources:
        if not _resource["uri"].startswith("site-"):
            _phases[_resource["uri"]] = _resource
            _uris.append(_resource["uri"])
    _phases_ret = []
    for uri in sorted(_uris):
        _phases_ret.append(_phases[uri])
    return _phases_ret


def total_power(site):
    _resources = siteResources_all(site, "Power Consumption")
    for _resource in _resources:
        if _resource["uri"].startswith("site-"):
            return _resource


def total_site(site,name):
    _resources = siteResources_all_exact(site, name)
    for _resource in _resources:
        if _resource["uri"].startswith("site-"):
            return _resource


def latest(resource):
    response = apiGetAuthorized('/v1/resource/' + str(resource["resourceId"]) + '/latest')
    return response.json()


def summary(resource):
    response = apiGetAuthorized('/v1/resource/' + str(resource["resourceId"]) + '/summary')
    return response.json()


def resource(uri):
    response = apiGetAuthorized('/v1/resource/uri/' + uri)
    return response.json()


def resources():
    response = apiGetAuthorized('/v1/resource')
    return response.json()["resources"]


def apiGetAuthorized(path):
    return requests.get(api_url + path, headers={'Authorization': 'Bearer ' + token["access_token"]})
