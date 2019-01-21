# -*- coding: utf-8 -*-
import requests
import os
import sys

sys.path.append(os.getcwd())


class SparkWorks:
    NAME_CONST = "name"
    UUID_CONST = "uuid"
    SYSTEM_NAME_CONST = "systemName"
    PHENOMENON_UUID_CONST = "phenomenonUuid"
    SITE_PREFIX_CONST = "site-"
    GAIA_CONST = "gaia-"
    DEV_CONST = "00"

    __api_url = "https://api.sparkworks.net"
    __sso_url = "https://sso.sparkworks.net/aa/oauth/token"
    __client_id = ""
    __client_secret = ""
    __username = ""
    __token = {}

    __the_groups = []
    __the_main_groups = []
    __the_phenomena = []
    __the_units = []
    __the_site_resources = {}

    def __init__(self, client_id=None, client_secret=None, api_url="https://api.sparkworks.net"):
        self.__api_url = api_url
        self.__client_id = client_id
        self.__client_secret = client_secret

    def connect(self, username, password):
        self.__username = username
        self.__token = self.getToken(username, password)

    def getToken(self, username, password):
        params = {'username': username, 'password': password, 'grant_type': "password", 'client_id': self.__client_id,
                  'client_secret': self.__client_secret}
        response = requests.post(self.__sso_url, params)
        return response.json()

    def groups(self):
        if len(self.__the_groups) != 0:
            return self.__the_groups
        else:
            response = self.apiGetAuthorized('/v2/group')
            self.__the_groups = response.json()
            return self.__the_groups

    def main_groups(self):
        if len(self.__the_main_groups) != 0:
            return self.__the_main_groups
        else:
            response = self.apiGetAuthorized('/v2/group/main')
            self.__the_main_groups = response.json()
            return self.__the_main_groups

    def group(self, uuid):
        if len(self.__the_groups) != 0:
            for group in self.__the_groups:
                if uuid == group[self.UUID_CONST]:
                    return group
        else:
            response = self.apiGetAuthorized('/v2/group/' + uuid)
            return response.json()

    def subGroups(self, group_uuid):
        response = self.apiGetAuthorized('/v2/group/' + group_uuid + '/subgroup/1')
        return response.json()

    def select_rooms(self, group_uuid, room_names):
        _rooms = []
        for room_name in room_names:
            for site in self.subGroups(group_uuid):
                if site[self.NAME_CONST].encode('utf-8') in room_name:
                    _rooms.append(site)
        return _rooms

    def phenomena(self):
        if len(self.__the_phenomena) != 0:
            return self.__the_phenomena
        else:
            response = self.apiGetAuthorized('/v2/phenomenon')
            self.__the_phenomena = response.json()
            return self.__the_phenomena

    def phenomenon(self, name):
        if len(self.__the_phenomena) != 0:
            for the_phenomenon in self.__the_phenomena:
                if name == the_phenomenon[self.NAME_CONST]:
                    return the_phenomenon
        else:
            response = self.apiGetAuthorized('/v2/phenomenon')
            self.__the_phenomena = response.json()
            for the_phenomenon in self.__the_phenomena:
                if name == the_phenomenon[self.NAME_CONST]:
                    return the_phenomenon

    def phenomenonByUuid(self, uuid):
        if len(self.__the_phenomena) != 0:
            for the_phenomenon in self.__the_phenomena:
                if uuid == the_phenomenon[self.UUID_CONST]:
                    return the_phenomenon
        else:
            response = self.apiGetAuthorized('/v2/phenomenon')
            self.__the_phenomena = response.json()
            for the_phenomenon in self.__the_phenomena:
                if uuid == the_phenomenon[self.UUID_CONST]:
                    return the_phenomenon

    def units(self):
        if len(self.__the_units) != 0:
            return self.__the_units
        else:
            response = self.apiGetAuthorized('/v2/unit')
            self.__the_units = response.json()
            return self.__the_units

    def unit(self, name):
        if len(self.__the_units) != 0:
            for the_unit in self.__the_units:
                if name == the_unit[self.NAME_CONST]:
                    return the_unit
        else:
            response = self.apiGetAuthorized('/v2/phenomenon')
            self.__the_units = response.json()
            for the_unit in self.__the_units:
                if name == the_unit[self.NAME_CONST]:
                    return the_unit

    def groupResources(self, group_uuid):
        if group_uuid not in self.__the_site_resources:
            response = self.apiGetAuthorized("/v2/group/" + group_uuid + "/resource")
            self.__the_site_resources[group_uuid] = response.json()
        return self.__the_site_resources[group_uuid]

    def groupAggResources(self, group_uuid):
        _resources = self.groupResources(group_uuid)
        _groupResources = []
        for _resource in _resources:
            if _resource[self.SYSTEM_NAME_CONST].startswith(self.SITE_PREFIX_CONST):
                _groupResources.append(_resource)
        return _groupResources

    def groupDeviceResources(self, group_uuid):
        _resources = self.groupResources(group_uuid)
        _groupResources = []
        for _resource in _resources:
            if _resource[self.SYSTEM_NAME_CONST].startswith(self.DEV_CONST):
                _groupResources.append(_resource)
        return _groupResources

    def groupRpiResources(self, group_uuid):
        _resources = self.groupResources(group_uuid)
        _groupResources = []
        for _resource in _resources:
            if _resource[self.SYSTEM_NAME_CONST].startswith(self.GAIA_CONST):
                _groupResources.append(_resource)
        return _groupResources

    def groupAggResource(self, group_uuid, phenomenon_uuid):
        _resources = self.groupAggResources(group_uuid)
        for _resource in _resources:
            if phenomenon_uuid == _resource[self.PHENOMENON_UUID_CONST]:
                return _resource

    def groupDeviceResource(self, group_uuid, phenomenon_uuid):
        _resources = self.groupDeviceResources(group_uuid)
        for _resource in _resources:
            if phenomenon_uuid == _resource[self.PHENOMENON_UUID_CONST]:
                return _resource

    def groupRpiDeviceResource(self, group_uuid, phenomenon_uuid):
        _resources = self.groupRpiResources(group_uuid)
        for _resource in _resources:
            if phenomenon_uuid == _resource[self.PHENOMENON_UUID_CONST]:
                return _resource

    def groupResources_all(self, group_uuid, phenomenon_uuid):
        _selected_resources = []
        _resources = self.groupResources(group_uuid)
        for _resource in _resources:
            if phenomenon_uuid == _resource[self.PHENOMENON_UUID_CONST]:
                _selected_resources.append(_resource)
        return _selected_resources

    def power_phases(self, group_uuid):
        _phases = {}
        _uris = []
        _resources = self.groupResources_all(group_uuid, self.phenomenon("Power Consumption")[self.UUID_CONST])
        for _resource in _resources:
            if not _resource[self.SYSTEM_NAME_CONST].startswith(self.SITE_PREFIX_CONST):
                _phases[_resource[self.SYSTEM_NAME_CONST]] = _resource
                _uris.append(_resource[self.SYSTEM_NAME_CONST])
        _phases_ret = []
        for uri in sorted(_uris):
            _phases_ret.append(_phases[uri])
        return _phases_ret

    def current_phases(self, group_uuid):
        _phases = {}
        _uris = []
        _resources = self.groupResources_all(group_uuid, self.phenomenon("Electrical Current")[self.UUID_CONST])
        for _resource in _resources:
            if not _resource[self.SYSTEM_NAME_CONST].startswith(self.SITE_PREFIX_CONST):
                _phases[_resource[self.SYSTEM_NAME_CONST]] = _resource
                _uris.append(_resource[self.SYSTEM_NAME_CONST])
        _phases_ret = []
        for uri in sorted(_uris):
            _phases_ret.append(_phases[uri])
        return _phases_ret

    def total_power(self, site):
        _resources = self.groupResources_all(site, self.phenomenon("Power Consumption")[self.UUID_CONST])
        for _resource in _resources:
            if _resource[self.SYSTEM_NAME_CONST].startswith(self.SITE_PREFIX_CONST):
                return _resource

    def latest(self, resource_uuid):
        response = self.apiGetAuthorized('/v2/resource/' + resource_uuid + '/latest')
        return response.json()

    def summary(self, resource_uuid):
        response = self.apiGetAuthorized('/v2/resource/' + resource_uuid + '/summary')
        return response.json()

    def resourceBySystemName(self, system_name):
        response = self.apiPostAuthorized('/v2/resource/query', {self.SYSTEM_NAME_CONST: system_name})
        return response.json()

    def resourceByUuid(self, uuid):
        response = self.apiGetAuthorized('/v2/resource/' + uuid)
        return response.json()

    def resources(self):
        response = self.apiGetAuthorized('/v2/resource')
        return response.json()

    def apiGetAuthorized(self, path):
        return requests.get(self.__api_url + path, headers={'Authorization': 'Bearer ' + self.__token["access_token"]})

    def apiPostAuthorized(self, path, data):
        return requests.post(self.__api_url + path, headers={'Authorization': 'Bearer ' + self.__token["access_token"],
                                                             'Content-Type': 'application/json'}, json=data)
