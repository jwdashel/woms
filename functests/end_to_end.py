import requests
import xmltodict
import ast
import urllib.parse as urlencode

from tests import test_data

import func_test_helpers as helpers
from playout_systems import David, NexGen

stream = 'thefunk'
woms_whatson = f"https://api.demo.nypr.digital/whats-on/v1/whats-on?stream={stream}"


for playout_system in [NexGen(), David()]:
    print(f"TESTING WOMs & {playout_system}")

    playout = send_track(playout_system)

    whats_on_0, what_should_be_on_0 = next(playout)
    
    title = playout_system.norm_keys['title']
    composer = playout_system.norm_keys['composer']
    mm_uid = playout_system.norm_keys['mm_uid']

    helpers.assert_and_report("title", whats_on_0['title'], what_should_be_on_0[title])
    helpers.assert_and_report("composer", whats_on_0['mm_composer1'], what_should_be_on_0[composer])
    helpers.assert_and_report("ID", whats_on_0['mm_uid'], what_should_be_on_0[mm_uid])


    print(f"\nTESTING WOMs PLAYLIST HISTORY WITH {playout_system}")

    whats_on_1, what_should_be_on_1 = next(playout)

    php = whats_on_1['playlist_hist_preview']
    last_track = php[0]

    helpers.assert_and_report("last track title", last_track['title'], what_should_be_on_0[title])
    helpers.assert_and_report("last track composer", last_track['mm_composer1'], what_should_be_on_0[composer])
    helpers.assert_and_report("last track ID", last_track['mm_uid'], what_should_be_on_0[mm_uid])
    print()
    helpers.assert_and_report("current track title", whats_on_1['title'], what_should_be_on_1[title])
    helpers.assert_and_report("current track composer", whats_on_1['mm_composer1'], what_should_be_on_1[composer])
    helpers.assert_and_report("current track ID", whats_on_1['mm_uid'], what_should_be_on_1[mm_uid])
    print("\n")

