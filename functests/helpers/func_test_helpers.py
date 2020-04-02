import sys

offset = "\t\t"
woms_keys = {
    "title": "title",
    "composer": "composer",
    "mm_uid": "mm-uid"
}

def assert_and_report(element, one, another):
    print(f"{offset}  asserting that {element} is {one} ...")
    try:
        assert one == another
        print(f"{offset}\u2713 {one} is {element}!")
    except AssertionError as e:
        sys.exit(f"\nERROR: {element} {one} does not equal {another}!")

#TODO: report a failure gracefully

def assert_same_title(test_case_name, whatson, playout, system):
    response_title = whatson.get(woms_keys["title"])
    expected_title = playout.get(system.norm_keys["title"])

    assert_and_report(test_case_name, response_title, expected_title)

def assert_same_composer(test_case_name, whatson, playout, system): 
    response_composer = whatson.get(woms_keys["composer"])
    expected_composer = playout.get(system.norm_keys["composer"])

    assert_and_report(test_case_name, response_composer, expected_composer)

def assert_same_id(test_case_name, whatson, playout, system):
    response_mmid = whatson.get(woms_keys["mm_uid"])
    expected_mmid = playout.get(system.norm_keys["mm_uid"])

    assert_and_report(test_case_name, response_mmid, expected_mmid)
