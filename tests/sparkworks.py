# -*- coding: utf-8 -*-
import os
import sys
import requests


class SparkWorks:
    NAME_CONST = "name"
    UUID_CONST = "uuid"
    SYSTEM_NAME_CONST = "systemName"
    PHENOMENON_UUID_CONST = "phenomenonUuid"
    SITE_PREFIX_CONST = "site-"
    GAIA_CONST = "gaia-"
    DEV_CONST_XBEE = "00"
    DEV_CONST_LORA = "dragino-"
    SELECTION_DEPTH = 1
    SELECTION_DEPTH_MAX = 10
    SELECTION_PHASES = 3

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

    def subGroups(self, group_uuid, depth=SELECTION_DEPTH):
        response = self.apiGetAuthorized('/v2/group/' + group_uuid + '/subgroup/' + str(depth))
        return response.json()

    def select_room(self, group_uuid, room_name, max_depth=SELECTION_DEPTH_MAX):
        _room = None
        _depth = self.SELECTION_DEPTH
        room_name = room_name.decode('utf-8').strip()
        while _room is None:
            _subgroups = self.subGroups(group_uuid, _depth)
            _depth += 1
            for _subgroup in _subgroups:
                # Strip group name and replace it for match and sort to work on malformed group names
                _subgroup[self.NAME_CONST] = _subgroup[self.NAME_CONST].strip()
                _is_match = _subgroup[self.NAME_CONST] == room_name
                if _is_match:
                    _room = _subgroup
        return _room

    def select_rooms(self, group_uuid, room_names, max_depth=SELECTION_DEPTH_MAX, sort=True):
        _rooms = []
        _depth = self.SELECTION_DEPTH
        # Convert to unicode and strip so we don't have to do it twice below
        room_names = [r.decode('utf-8').strip() for r in room_names]
        while len(_rooms) != len(room_names) and _depth <= max_depth:
            _subgroups = self.subGroups(group_uuid, _depth)
            _depth += 1
            for _subgroup in _subgroups:
                # Strip group name and replace it for match and sort to work on malformed group names
                _subgroup[self.NAME_CONST] = _subgroup[self.NAME_CONST].strip()
                _is_match = _subgroup[self.NAME_CONST] in room_names
                _is_present = _subgroup in _rooms
                if _is_match and not _is_present:
                    _rooms.append(_subgroup)
        if sort is True:
            # To remember why and what I did here.
            # Since I am adjusting depth, the room list might not be ordered properly if
            # the rooms are in different level subgroups. For that reason I am ordering the
            # returned list of dicts by the name of the room and its index in the room_names list
            _rooms = sorted(_rooms, key=lambda room: room_names.index(room[self.NAME_CONST]))
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
            _is_rpi = _resource[self.SYSTEM_NAME_CONST].startswith(self.GAIA_CONST)
            _is_xbee = _resource[self.SYSTEM_NAME_CONST].startswith(self.DEV_CONST_XBEE)
            _is_lora = _resource[self.SYSTEM_NAME_CONST].startswith(self.DEV_CONST_LORA)
            if _is_rpi or _is_xbee or _is_lora:
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
        _resources = self.groupResources_all(group_uuid, self.phenomenon("Calculated Power Consumption")[self.UUID_CONST])
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

    def select_power_meter(self, group_uuid, room_name, phases_max=SELECTION_PHASES):
        _phases = []
        _groups = self.subGroups(group_uuid, self.SELECTION_DEPTH_MAX)
        _groups.append(self.group(group_uuid))
        _room = self.select_room(group_uuid, room_name)
        _group = _room
        while not _phases:
            _phases = self.current_phases(_group['uuid'])
            if _group['uuid'] == group_uuid:
                if len(_phases) > phases_max:
                    _phases = []
                break
            for _g in _groups:
                if _group['parentPath'] == _g['path']:
                    _group = _g
                    break
        return _room, _phases

    def latest(self, resource_uuid):
        response = self.apiGetAuthorized('/v2/resource/' + resource_uuid + '/latest')
        return response.json()

    def summary(self, resource_uuid):
        response = self.apiGetAuthorized('/v2/resource/' + resource_uuid + '/summary')
        return response.json()

    def timerange(self, resource_uuid, start_date, end_date, granularity="5min"):
        _queries = {"queries": []}
        for uuid in resource_uuid:
            _query = {"from": start_date.timestamp()*1000,
                      "to": end_date.timestamp()*1000,
                      "resourceUuid": resource_uuid,
                      "resultLimit": None,
                      "granularity": granularity}
            _queries["queries"].append(_query)
        response = self.apiPostAuthorized('/v2/resource/query/timerange', _queries)
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
