offset = "\t\t"
def assert_and_report(element, one, another):
    print(f"{offset}  asserting that {element} is {one} ...")
    assert one == another
    print(f"{offset}\u2713 {one} is {element}!")


def send_track(playout_system):
    for sample_input in playout_system.sample_inputs():

        print("\tsending new track to woms ...", end=' ')

        r = playout_system.update_track(sample_input)
        print(f"{r.status_code}\n")
        assert r.status_code == 200

        print("\tasserting WOMs knows what's on ...", end=' ')

        r = requests.get(woms_whatson)
        print(f"{r.status_code}")
        assert r.status_code == 200

        whats_on = ast.literal_eval(r.text)['data']['attributes']

        yield whats_on, playout_system.reference_track(sample_input)
