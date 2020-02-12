import requests
import xmltodict
import ast
import urllib.parse as urlencode

from tests import test_data

import func_test_helpers as helpers

stream = 'thefunk'

# TODO: readjust input index
nexgen_inputs = [
    test_data.nexgen_sample(),
    test_data.nexgen_sample_2()
]

david_inputs = [
    test_data.david_sample()
]

woms_whatson = f"https://api.demo.nypr.digital/whats-on/v1/whats-on?stream={stream}"

def send_track(nexgen_inputs):
    for nexgen_input in nexgen_inputs:

        nexgendata_encoded = urlencode.quote(nexgen_input)
        nexgendata = dict(dict(xmltodict.parse(nexgen_input))['audio'])
        woms_update = f"https://api.demo.nypr.digital/whats-on/v1/update?stream={stream}&xml_contents={nexgendata_encoded}"

        print("\tsending new track to woms ...", end=' ')

        r = requests.get(woms_update)
        print(f"{r.status_code}\n")
        assert r.status_code == 200

        print("\tasserting WOMs knows what's on ...", end=' ')

        r = requests.get(woms_whatson)
        print(f"{r.status_code}")
        assert r.status_code == 200

        whats_on = ast.literal_eval(r.text)['data']['attributes']

        yield whats_on, nexgendata


def send_david_track(david_inputs):
    for david_input in david_inputs:
        daviddata = dict(xmltodict.parse(david_input))
        present_track = next(filter(lambda x: x['@sequence'] == 'present', daviddata['wddxPacket']['item']))
        woms_update = f"https://api.demo.nypr.digital/whats-on/v1/update?stream={stream}"

        print("\tsending new track to woms ...", end=' ')
        r = requests.post(woms_update, data=david_input.encode('utf-8'))
        print(f"{r.status_code}\n")
        assert r.status_code == 200

        print("\tasserting WOMs knows what's on ...", end=' ')

        r = requests.get(woms_whatson)
        print(f"{r.status_code}")
        assert r.status_code == 200

        whats_on = ast.literal_eval(r.text)['data']['attributes']

        yield whats_on, present_track


playout = send_track(nexgen_inputs)


print("TESTING WOMs & NEXGEN\n")
whats_on_0, what_should_be_on_0 = next(playout)

helpers.assert_and_report("title", whats_on_0['title'], what_should_be_on_0['title'])
helpers.assert_and_report("composer", whats_on_0['mm_composer1'], what_should_be_on_0['comment1'])
helpers.assert_and_report("ID", whats_on_0['mm_uid'], what_should_be_on_0['number'])

print("\n\ttesting that woms has playlist history\n")

whats_on_1, what_should_be_on_1 = next(playout)

php = whats_on_1['playlist_hist_preview']
last_track = php[0]
helpers.assert_and_report("last track title", last_track['title'], what_should_be_on_0['title'])
helpers.assert_and_report("last track composer", last_track['mm_composer1'], what_should_be_on_0['comment1'])
helpers.assert_and_report("last track ID", last_track['mm_uid'], what_should_be_on_0['number'])
print()
helpers.assert_and_report("current track title", whats_on_1['title'], what_should_be_on_1['title'])
helpers.assert_and_report("current track composer", whats_on_1['mm_composer1'], what_should_be_on_1['comment1'])
helpers.assert_and_report("current track ID", whats_on_1['mm_uid'], what_should_be_on_1['number'])

print("\n\nTESTING WOMs & DAViD\n")

david_playout = send_david_track(david_inputs)

whats_on_0, what_should_be_on_0 = next(david_playout)

helpers.assert_and_report("title", whats_on_0['title'], what_should_be_on_0['Title'])
helpers.assert_and_report("composer", whats_on_0['mm_composer1'], what_should_be_on_0['Music_Composer'])
helpers.assert_and_report("ID", whats_on_0['mm_uid'], what_should_be_on_0['Music_MusicID'])

print("\nwham, bam, thank you, ma'am!", end='\n\n')

