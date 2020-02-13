offset = "\t\t"
woms_keys = {
    "title": "title",
    "composer": "mm_composer1",
    "mm_uid": "mm_uid"
}

def assert_and_report(element, one, another):
    print(f"{offset}  asserting that {element} is {one} ...")
    assert one == another
    print(f"{offset}\u2713 {one} is {element}!")

#TODO: report a failure gracefully

assert_same_title = lambda test_case_name, whatson, playout, system: assert_and_report(test_case_name,
        whatson.get(woms_keys["title"]), playout.get(system.norm_keys["title"]))

assert_same_composer = lambda test_case_name, whatson, playout, system: assert_and_report(test_case_name,
        whatson.get(woms_keys["composer"]), playout.get(system.norm_keys["composer"]))

assert_same_id = lambda test_case_name, whatson, playout, system: assert_and_report(test_case_name,
        whatson.get(woms_keys["mm_uid"]), playout.get(system.norm_keys["mm_uid"]))
