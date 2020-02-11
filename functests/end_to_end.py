import requests
import xmltodict
import ast
import urllib.parse as urlencode

from tests import test_data

import func_test_helpers as helpers

stream = 'thefunk'

nexgendata_raw = test_data.nexgen_sample()
nexgendata_encoded = urlencode.quote(nexgendata_raw)
nexgendata = dict(dict(xmltodict.parse(nexgendata_raw))['audio'])

nexgendata_raw_2 = test_data.nexgen_sample_2()
nexgendata_encoded_2 = urlencode.quote(nexgendata_raw_2)
nexgendata_2 = dict(dict(xmltodict.parse(nexgendata_raw_2))['audio'])

# woms song swan song
woms_song_0 = f"https://api.demo.nypr.digital/whats-on/v1/update?stream={stream}&xml_contents={nexgendata_encoded}"
woms_song_1 = f"https://api.demo.nypr.digital/whats-on/v1/update?stream={stream}&xml_contents={nexgendata_encoded_2}"
woms_whatson = f"https://api.demo.nypr.digital/whats-on/v1/whats-on?stream={stream}"

print("TESTING WOMS & NEXGEN\n")
print("\tsending new track to woms ...", end=' ')
r = requests.get(woms_update)
print(f"{r.status_code}")
assert r.status_code == 200

print("\n\tasserting WOMs knows what's on ...", end=' ')
r = requests.get(woms_whatson)
print(f"{r.status_code}")
assert r.status_code == 200
whatson = ast.literal_eval(r.text)['data']['attributes']
helpers.assert_and_report("title", whatson['title'], nexgendata['title'])
helpers.assert_and_report("composer", whatson['mm_composer1'], nexgendata['comment1'])
helpers.assert_and_report("ID", whatson['mm_uid'], nexgendata['number'])

print("\n\ttesting that woms has playlist history")


print("\nwham, bam, thank you, ma'am!", end='\n\n')



