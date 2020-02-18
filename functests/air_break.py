from tests import test_data

import helpers.func_test_helpers as helpers
from helpers.playout_systems import David, NexGen, send_track

david_inputs = [
    test_data.david_sample(0),
    test_data.david_airbreak(),
    test_data.david_sample(1)
]
nexgen_inputs = [
    test_data.nexgen_sample_0(),
    test_data.nexgen_airbreak(),
    test_data.nexgen_sample_1(),
]


for playout_system in [NexGen(nexgen_inputs), David(david_inputs)]:
    print(f"TESTING WOMs AIRBREAKS WITH {playout_system}")

    playout = send_track(playout_system)
    whats_on, what_should_be_on = next(playout)
    
    helpers.assert_same_title("title", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_composer("composer", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_id("id", whats_on, what_should_be_on, playout_system)

    airbreak, _ = next(playout)
    helpers.assert_and_report("air break", True, airbreak['air_break'])

    after_airbreak_track, expected_after_airbreak_track = next(playout)

    php = after_airbreak_track['playlist_hist_preview']
    pre_airbreak_track = php[0]

    helpers.assert_same_title("pre-airbreak track title", pre_airbreak_track, what_should_be_on, playout_system)
    helpers.assert_same_title("post-airbreak track title", after_airbreak_track, expected_after_airbreak_track, playout_system)

