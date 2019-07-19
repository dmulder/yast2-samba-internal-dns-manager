from yast import import_module
import_module('SambaToolDnsAPI')
from yast import SambaToolDnsAPI
from samba.netcmd import CommandError

class Connection:
    def __init__(self, lp, creds, server):
        self.lp = lp
        self.creds = creds
        self.server = server
        self.__refresh_zones()

    def __refresh_zones(self):
        self.zones = SambaToolDnsAPI.zonelist(self.server, self.creds.get_username(), self.creds.get_password())
        self._forward = {zone: self.zones[zone] for zone in self.zones.keys() if 'DNS_RPC_ZONE_REVERSE' not in self.zones[zone]['Flags']}
        self._reverse = {zone: self.zones[zone] for zone in self.zones.keys() if 'DNS_RPC_ZONE_REVERSE' in self.zones[zone]['Flags']}
        if len(self.zones.keys()) == 0:
            raise CommandError('Failed to authenticate to list dns zones')

    def forward_zones(self):
        return self._forward

    def reverse_zones(self):
        return self._reverse

    def records(self, selection):
        if selection in self._forward or selection in self._reverse:
            return SambaToolDnsAPI.query(self.server, selection, '@', 'ALL', self.creds.get_username(), self.creds.get_password())
        else:
            matching_zones = [zone for zone in list(self._forward.keys()) + list(self._reverse.keys()) if selection[-len(zone):] == zone]
            zone = max(matching_zones, key=len)
            return SambaToolDnsAPI.query(self.server, zone, selection, 'ALL', self.creds.get_username(), self.creds.get_password())
