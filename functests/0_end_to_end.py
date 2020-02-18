from tests import test_data

import helpers.func_test_helpers as helpers
from helpers.playout_systems import David, NexGen

david_inputs = [
    test_data.david_sample(),
]
nexgen_inputs = [
    test_data.nexgen_sample(),
]

for playout_system in [NexGen(nexgen_inputs), David(david_inputs)]:
    print(f"TESTING WOMs & {playout_system}")

    playout = playout_system.queue_tracks()
    whats_on, what_should_be_on = next(playout)
    
    helpers.assert_same_title("title", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_composer("composer", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_id("id", whats_on, what_should_be_on, playout_system)
