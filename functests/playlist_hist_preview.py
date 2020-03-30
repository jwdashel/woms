from tests import test_data

import helpers.func_test_helpers as helpers
from helpers.playout_systems import David, NexGen

david_inputs = [
    test_data.david_sample(0),
    test_data.david_sample(1),
]
nexgen_inputs = [
    test_data.nexgen_sample_0(),
    test_data.nexgen_sample_1(),
]


for playout_system in [NexGen(nexgen_inputs), David(david_inputs)]:
    print(f"TESTING WOMs PLAYLIST HISTORY WITH {playout_system}")
    playout = playout_system.queue_tracks()
    whats_on, what_should_be_on = next(playout)
    whats_on = whats_on['included'][0]['attributes']
    
    helpers.assert_same_title("title", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_composer("composer", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_id("id", whats_on, what_should_be_on, playout_system)


    next_whatson, what_should_be_on_next = next(playout)
    next_whatson = next_whatson['included']
    
    last_track = next_whatson[1]['attributes']
    whats_on_next = next_whatson[0]['attributes']
    

    helpers.assert_same_title("last track title", last_track, what_should_be_on, playout_system)
    helpers.assert_same_composer("last track composer", last_track, what_should_be_on, playout_system)
    helpers.assert_same_id("last track id", last_track, what_should_be_on, playout_system)

    print()

    helpers.assert_same_title("current track title", whats_on_next, what_should_be_on_next, playout_system)
    helpers.assert_same_composer("current track composer", whats_on_next, what_should_be_on_next, playout_system)
    helpers.assert_same_id("current track id", whats_on_next, what_should_be_on_next, playout_system)
