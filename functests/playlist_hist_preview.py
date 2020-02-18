from tests import test_data

import helpers.func_test_helpers as helpers
from helpers.playout_systems import David, NexGen, send_track

david_inputs = [
    test_data.david_sample(0),
    test_data.david_sample(1),
]
nexgen_inputs = [
    test_data.nexgen_sample(),
    test_data.nexgen_sample_2(),
]


for playout_system in [NexGen(nexgen_inputs), David(david_inputs)]:
    print(f"TESTING WOMs PLAYLIST HISTORY WITH {playout_system}")
    playout = send_track(playout_system)
    whats_on, what_should_be_on = next(playout)
    
    helpers.assert_same_title("title", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_composer("composer", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_id("id", whats_on, what_should_be_on, playout_system)


    whats_on_next, what_should_be_on_next = next(playout)
    
    php = whats_on_next['playlist_hist_preview']
    last_track = php[0]

    helpers.assert_same_title("last track title", last_track, what_should_be_on, playout_system)
    helpers.assert_same_composer("last track composer", last_track, what_should_be_on, playout_system)
    helpers.assert_same_id("last track id", last_track, what_should_be_on, playout_system)

    print()

    helpers.assert_same_title("current track title", whats_on_next, what_should_be_on_next, playout_system)
    helpers.assert_same_composer("current track composer", whats_on_next, what_should_be_on_next, playout_system)
    helpers.assert_same_id("current track id", whats_on_next, what_should_be_on_next, playout_system)
