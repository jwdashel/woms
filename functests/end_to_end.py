from tests import test_data

import func_test_helpers as helpers
from playout_systems import David, NexGen, send_track



for playout_system in [NexGen(), David()]:
    print(f"TESTING WOMs & {playout_system}")

    playout = send_track(playout_system)
    whats_on, what_should_be_on = next(playout)
    
    helpers.assert_same_title("title", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_composer("composer", whats_on, what_should_be_on, playout_system)
    helpers.assert_same_id("id", whats_on, what_should_be_on, playout_system)

    print(f"\nTESTING WOMs PLAYLIST HISTORY WITH {playout_system}")

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

    print()
    airbreak, _ = next(playout)
    helpers.assert_and_report("air break", True, airbreak['air_break'])

    after_airbreak_track, expected_after_airbreak_track = next(playout)

    php = after_airbreak_track['playlist_hist_preview']
    pre_airbreak_track = php[0]

    helpers.assert_same_title("pre-airbreak track title", pre_airbreak_track, what_should_be_on_next, playout_system)
    helpers.assert_same_title("post-airbreak track title", after_airbreak_track, expected_after_airbreak_track, playout_system)

    print("\n")

print("wham, bam, thank you, ma'am")

