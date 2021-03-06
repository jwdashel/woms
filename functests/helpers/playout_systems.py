from tests import test_data
import urllib.parse as urlencode
import requests
import xmltodict
import json
import time

stream = 'func_tests'
woms_whatson = f"https://nla6c7i6p7.execute-api.us-east-1.amazonaws.com/demo/whats-on/v1/whats-on?stream={stream}"


class PlayoutSystem(object):
    def __init__(self, data):
        self.inputs = data

    def sample_inputs(self):
        return self.inputs

    def update_track(self, sample_input):
        raise NotImplementedError()

    def reference_track(self, sample_input):
        raise NotImplementedError()

    def __str__(self):
        return self.name

    def queue_tracks(self):
        for sample_input in self.sample_inputs():

            print("\tsending new track to WOMs ...", end=' ')

            r = self.update_track(sample_input)
            print(f"{r.status_code}\n")
            assert r.status_code == 200

            print("\tasserting WOMs knows what's on ...", end=' ')

            r = requests.get(woms_whatson)
            print(f"{r.status_code}")
            assert r.status_code == 200

            whats_on = json.loads(r.text)

            yield whats_on, self.reference_track(sample_input)

class David(PlayoutSystem):
    name = "DAVID"
    norm_keys = {
        "title": "Title",
        "composer": "Music_Composer",
        "mm_uid": "Music_MusicID"
    }

    def update_track(self, sample_input):
        woms_update = f"https://nla6c7i6p7.execute-api.us-east-1.amazonaws.com/demo/whats-on/v1/update?stream={stream}"
        return requests.post(woms_update, data=sample_input.encode('utf-8'))

    def reference_track(self, sample_input):
        daviddata = dict(xmltodict.parse(sample_input))
        return next(filter(lambda x: x['@sequence'] == 'present', daviddata['wddxPacket']['item']))

class NexGen(PlayoutSystem):
    name = "NEXGEN"
    norm_keys = {
        "title": "title",
        "composer": "comment1",
        "mm_uid": "number"
    }

    def update_track(self, sample_input):
        nexgendata_encoded = urlencode.quote(sample_input)
        woms_update = f"https://nla6c7i6p7.execute-api.us-east-1.amazonaws.com/demo/whats-on/v1/update?stream={stream}&xml_contents={nexgendata_encoded}"
        return requests.get(woms_update)

    def reference_track(self, sample_input):
        return dict(dict(xmltodict.parse(sample_input))['audio'])

