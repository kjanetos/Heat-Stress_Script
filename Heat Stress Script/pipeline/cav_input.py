CAV_TABLE = {
    1: ("Short sleeves and pants", -1),
    2: ("Work clothes (long sleeve shirt and pants)", 0),
    3: ("Cloth coveralls", 0),
    4: ("SMS polypropylene coveralls", 0.5),
    5: ("Polyolefin coveralls", 1),
    6: ("Double-layer woven clothing", 3),
    7: ("Limited-use vapour-barrier coveralls", 11),
    8: ("Adding a hood (full head and neck covering; not face)", 1),
}


def select_cav(pid, day):

    print(f"\nParticipant {pid} Day {day}")

    for number, (name, cav) in CAV_TABLE.items():
        print(f"{number}. {name} ({cav:+}°C)")

    while True:
        try:
            choice = int(input("Select Clothing: "))
            if choice in CAV_TABLE:
                return CAV_TABLE[choice]
        except ValueError:
            pass

        print("Invalid selection.")