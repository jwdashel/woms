class PlayoutSystem(object):
    def sample_inputs(self):
        return self.inputs

    def update_track(self, sample_input):
        raise NotImplementedError()

    def update_track(self, sample_input):
        raise NotImplementedError()

    def __str__(self):
        return self.name

class David(PlayoutSystem):
    name = "DAViD"
    inputs = [
        test_data.david_sample(0),
        test_data.david_sample(1)
    ]
    norm_keys = {
        "title": "Title",
        "composer": "Music_Composer",
        "mm_uid": "Music_MusicID"
    }

    def update_track(self, sample_input):
        woms_update = f"https://api.demo.nypr.digital/whats-on/v1/update?stream={stream}"
        return requests.post(woms_update, data=sample_input.encode('utf-8'))

    def reference_track(self, sample_input):
        daviddata = dict(xmltodict.parse(sample_input))
        return next(filter(lambda x: x['@sequence'] == 'present', daviddata['wddxPacket']['item']))

class NexGen(PlayoutSystem):
    name = "NexGen"
    # TODO: readjust input index
    inputs = [
        test_data.nexgen_sample(),
        test_data.nexgen_sample_2()
    ]
    norm_keys = {
        "title": "title",
        "composer": "comment1",
        "mm_uid": "number"
    }

    def update_track(self, sample_input):
        nexgendata_encoded = urlencode.quote(sample_input)
        woms_update = f"https://api.demo.nypr.digital/whats-on/v1/update?stream={stream}&xml_contents={nexgendata_encoded}"
        return requests.get(woms_update)

    def reference_track(self, sample_input):
        return dict(dict(xmltodict.parse(sample_input))['audio'])
