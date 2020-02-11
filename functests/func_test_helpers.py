offset = "\t\t"
def assert_and_report(element, one, another):
    print(f"{offset}  asserting that {element} is {one} ...")
    assert one == another
    print(f"{offset}\u2713 {one} is {element}!")
