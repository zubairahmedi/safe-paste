"""Builds the test set: 200 made-up case notes with every personal detail marked (ground truth).

    python research/make_notes.py      -> research/notes.jsonl

All values are fake by construction:
  phones use 555-01xx (reserved for fiction in North America) and UK Ofcom drama numbers (07700 900xxx),
  NHS numbers use the 999 test range, SINs start with 0, SSNs start with 9 (never issued),
  emails use example.org / example.com, card numbers are standard test cards.
Seeded, so the same set is rebuilt every time.
"""
import json
import pathlib
import random

R = random.Random(2026)
OUT = pathlib.Path(__file__).resolve().parent / "notes.jsonl"

FIRST = ["Amina", "Yusuf", "Fatima", "Hamid", "Zahra", "Reza", "Leila", "Abdi", "Hodan", "Ayaan", "Selam", "Dawit",
         "Priya", "Arjun", "Harpreet", "Gurpreet", "Maria", "Jose", "Lucia", "Wei", "Mei", "Olena", "Taras", "Kwame",
         "Ama", "Chinedu", "Ngozi", "Liam", "Emma", "Noah", "Olivia", "Siobhan", "Niamh", "Declan", "Aoife", "Mateo",
         "Sofia", "Daniel", "Hannah", "Omar", "Layla", "Tariq", "Nadia", "Samir", "Ines"]
LAST = ["Rahimi", "Hassan", "Ahmadi", "Karimi", "Mohamed", "Abdullahi", "Tesfaye", "Gebremedhin", "Singh", "Kaur",
        "Patel", "Sharma", "Garcia", "Rodriguez", "Chen", "Wang", "Kovalenko", "Shevchenko", "Mensah", "Okafor",
        "Nwosu", "O'Neill", "Murphy", "MacDonald", "Smith", "Brown", "Tremblay", "Gagnon", "Nguyen", "Tran", "Haddad",
        "Khoury", "Ali", "Osei", "Bakr", "Morales"]
HYPHEN_FIRST = ["Jean-Pierre", "Marie-Claude", "Anne-Marie", "Jean-Luc"]
HYPHEN_LAST = ["Al-Hassan", "Smith-Jones", "Abu-Bakr", "Lopez-Garcia"]
WORD_NAMES = ["Grace", "Hope", "Faith", "Joy", "Rose", "Will", "Dawn", "Summer", "Sky", "Bill", "Mark", "Hunter"]
NONLATIN = ["أمينة رحيمي", "يوسف حسن", "زهرا کریمی", "فاطمه احمدی", "ሰላም ተስፋዬ"]
STAFF = ["Okafor", "Patel", "Nguyen", "Tremblay", "Haddad", "MacDonald", "Chen", "Singh"]
STREETS = ["Birchmount Road", "King St W", "Albert Road", "Maple Avenue", "Danforth Ave", "Weston Road", "Lawrence Ave E",
           "Queen Street", "Bloor St W", "Victoria Park Ave", "Oak Lane", "Elm Drive", "Kennedy Road", "Jane Street"]
CA_POSTAL = ["M1N 3J5", "M6H 2B4", "M4C 1A8", "L1S 2K7", "M9N 3E2", "V5K 0A1", "T2P 1J9", "K1A 0B1"]
UK_POSTAL = ["LS6 2AB", "M1 1AE", "B33 8TH", "SW1A 1AA", "CR2 6XH", "DN55 1PT", "E1 6AN"]
US_ZIP = [("TX", "78701"), ("NY", "10027"), ("WA", "98103"), ("IL", "60614")]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DESCRIPTIONS = [
    "She is the only Tigrinya speaking mother of triplets at our Jane and Finch site.",
    "He's the deacon at the church on Weston whose wife passed in the spring.",
    "She's the 14 year old who was suspended after the fire in the Westview gym.",
    "He's the only Syrian dentist retraining through our program this year.",
    "She drives the pink school bus on the Lawrence route and lives above the pharmacy.",
    "He's the former city councillor's nephew who was in the news last month.",
    "She is the only resident on the third floor who uses a guide dog.",
    "He coaches the under 12 cricket team at the community centre on Sundays.",
]


def luhn_complete(prefix_digits):
    """Append the Luhn check digit."""
    digits = [int(d) for d in prefix_digits]
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return prefix_digits + str((10 - total % 10) % 10)


def nhs_number():
    while True:
        d = "999" + "".join(str(R.randint(0, 9)) for _ in range(6))
        s = sum(int(d[i]) * (10 - i) for i in range(9))
        c = 11 - s % 11
        c = 0 if c == 11 else c
        if c != 10:
            n = d + str(c)
            return f"{n[:3]} {n[3:6]} {n[6:]}"


class Note:
    def __init__(self, nid, style, region):
        self.id, self.style, self.region = nid, style, region
        self.text, self.entities = "", []

    def add(self, s, kind=None, group=None):
        if kind:
            self.entities.append({"kind": kind, "group": group, "value": s, "start": len(self.text), "end": len(self.text) + len(s)})
        self.text += s
        return self

    def json(self):
        return {"id": self.id, "style": self.style, "region": self.region, "text": self.text, "entities": self.entities}


def phone(region):
    if region == "UK":
        n = f"07700 900{R.randint(0, 999):03d}"
        return R.choice([(n, "phone_uk"), ("+44 " + n[1:], "phone_uk_intl")])
    line = f"01{R.randint(0, 99):02d}"
    area = R.choice(["416", "647", "905", "604", "613"])
    return R.choice([
        (f"({area}) 555-{line}", "phone_paren"), (f"{area}-555-{line}", "phone_dash"),
        (f"{area}.555.{line}", "phone_dots"), (f"{area}555{line}", "phone_plain"),
        (f"+1 {area} 555 {line}", "phone_intl")])


def dob():
    y, m, d = R.randint(1950, 2012), R.randint(1, 12), R.randint(1, 28)
    sfx = "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return R.choice([
        (f"{y}-{m:02d}-{d:02d}", "dob_iso"), (f"{d:02d}/{m:02d}/{y}", "dob_slash"),
        (f"{MONTHS[m - 1]} {d}, {y}", "dob_long"), (f"{d}{sfx} {MONTHS[m - 1]} {y}", "dob_day_month"),
        (f"{d:02d}/{m:02d}/{str(y)[2:]}", "dob_two_digit_year")])


def build(nid):
    region = R.choices(["ON", "BC", "UK", "US"], weights=[50, 15, 25, 10])[0]
    style = R.choices(["case_note", "email", "referral", "text"], weights=[45, 20, 15, 20])[0]
    n = Note(nid, style, region)
    first, last = R.choice(FIRST), R.choice(LAST)
    if R.random() < 0.08:
        first = R.choice(HYPHEN_FIRST)
    if R.random() < 0.08:
        last = R.choice(HYPHEN_LAST)
    if R.random() < 0.15:
        first = R.choice(WORD_NAMES)
    full = f"{first} {last}"
    staff = R.choice(STAFF)

    if style == "text":
        # texting style: lowercase names, no capitals, run on
        n.add("spoke w ").add(full.lower(), "name_lowercase", "Lowercase names").add(" again today, ")
        p, k = phone(region)
        n.add("her cell is ").add(p, k, "Phone numbers").add(" now not the old one. ")
        if R.random() < 0.5:
            n.add("lives at ")
            num = R.randint(10, 999)
            n.add(f"{num} {R.choice(STREETS).lower()}", "address_lowercase", "Street addresses").add(". ")
        n.add("tell ").add(first.lower(), "name_lowercase", "Lowercase names").add(" to bring her id thurs")
        if R.random() < 0.4:
            n.add(" and the papers from ").add(R.choice(STAFF), "name_single_mid", "Single names (mid sentence)")
        n.add(".")
        return n

    header = R.random() < 0.15
    if header:
        n.add("CLIENT: ").add(full.upper(), "name_allcaps", "ALL CAPS names").add("\n")

    opener = {"case_note": "Met with ", "email": "Hi team, quick update on ", "referral": "I'm referring "}[style]
    n.add(opener).add(full, "name_hyphen" if "-" in full else ("name_word_full" if first in WORD_NAMES else "name_full"),
                      "Full names")
    if R.random() < 0.6:
        v, k = dob()
        n.add(" (DOB ").add(v, k, "Dates of birth").add(")")
    n.add(" at the office today." if style != "referral" else " to your program.")

    # identifiers
    if region in ("ON", "BC", "US") and R.random() < 0.55:
        if region == "ON":
            if R.random() < 0.6:
                hc = f"{R.randint(1000, 9999)}-{R.randint(100, 999)}-{R.randint(100, 999)}-{R.choice(['AB', 'XY', 'KM', 'ZT'])}"
                n.add(" OHIP ").add(hc, "health_card_ohip", "ID and health numbers").add(".")
            else:
                hc = f"{R.randint(1000, 9999)} {R.randint(100, 999)} {R.randint(100, 999)}"
                n.add(" Health card ").add(hc, "health_card_no_version", "ID and health numbers").add(".")
        elif region == "BC":
            n.add(" PHN ").add(f"9{R.randint(100, 999)} {R.randint(100, 999)} {R.randint(100, 999)}", "health_card_bc_phn", "ID and health numbers").add(".")
        else:
            n.add(" SSN ").add(f"9{R.randint(10, 99)}-{R.randint(10, 99)}-{R.randint(1000, 9999)}", "ssn", "ID and health numbers").add(".")
    if region == "UK" and R.random() < 0.85:
        if R.random() < 0.45:
            n.add(" NHS number ").add(nhs_number(), "nhs", "ID and health numbers").add(".")
        else:
            letters = R.choice(["AB", "CE", "JG", "KR", "TW", "PR"])
            n.add(" NI number ").add(f"{letters} {R.randint(10, 99)} {R.randint(10, 99)} {R.randint(10, 99)} {R.choice('ABCD')}", "ni_number", "ID and health numbers").add(".")
    if region in ("ON", "BC") and R.random() < 0.25:
        sin = luhn_complete("0" + "".join(str(R.randint(0, 9)) for _ in range(7)))
        n.add(" SIN ").add(f"{sin[:3]} {sin[3:6]} {sin[6:]}", "sin", "ID and health numbers").add(".")
    if R.random() < 0.35:
        cid = R.choice([f"C-{R.randint(1000, 9999)}", f"{R.randint(10000, 99999)}", f"2026-{R.randint(1000, 9999)}"])
        lead = R.choice(["Client ID ", "File # ", "Case number "])
        n.add(" " + lead).add(cid, "client_id", "ID and health numbers").add(".")

    # family + names in context
    if R.random() < 0.5:
        rel = R.choice(["son", "daughter", "husband", "sister", "mother"])
        kid = R.choice(FIRST + WORD_NAMES)
        n.add(f"\nHer {rel} ").add(kid, "name_context", "Names after family words").add(" is on the waitlist for counselling.")
    # first name used alone (after the full name)
    n.add("\n").add(first, "name_first_after_full", "First names after the full name").add(R.choice([
        " said the school keeps calling about attendance.", " missed the last two appointments.",
        " asked about the food bank hours.", " needs a letter for the landlord."]))

    # contact
    if R.random() < 0.7:
        p, k = phone(region)
        n.add(" Best number is ").add(p, k, "Phone numbers").add(".")
    if R.random() < 0.45:
        e = f"{first.lower().replace('-', '')}.{last.lower().replace(chr(39), '').replace('-', '')}@example.org"
        n.add(" Email ").add(e, "email", "Emails").add(".")

    # address
    if R.random() < 0.55:
        num = R.randint(2, 4999)
        street = R.choice(STREETS)
        shape = R.random()
        n.add(" She lives at ")
        if region == "UK" and shape < 0.5:
            n.add(f"Flat {R.randint(1, 20)}, {num} {street}", "address_flat_first", "Street addresses")
        elif shape < 0.25 and region != "UK":
            n.add(f"{R.randint(100, 2999)}-{num} {street}", "address_unit_dash", "Street addresses")
        elif shape < 0.55:
            n.add(f"{num} {street}, Apt {R.randint(1, 30)}", "address_unit_after", "Street addresses")
        else:
            n.add(f"{num} {street}", "address_basic", "Street addresses")
        if region in ("ON", "BC"):
            n.add(", Toronto ON " if region == "ON" else ", Vancouver BC ")
            pc = R.choice(CA_POSTAL)
            if R.random() < 0.25:
                pc = pc.replace(" ", "").lower()
                n.add(pc, "postcode_ca_lowercase", "Postcodes")
            else:
                n.add(pc, "postcode_ca", "Postcodes")
        elif region == "UK":
            n.add(", Leeds ").add(R.choice(UK_POSTAL), "postcode_uk", "Postcodes")
        else:
            st, z = R.choice(US_ZIP)
            n.add(f", Austin {st} ").add(z, "zip_us", "Postcodes")
        n.add(".")

    # staff names with titles, single names
    if R.random() < 0.5:
        n.add(" Follow up with ").add(R.choice(["Ms. ", "Dr. ", "Mr. "]))
        n.add(staff, "name_title", "Names after a title (Ms., Dr.)").add(" next week.")
    if R.random() < 0.35:
        other = R.choice(FIRST)
        n.add(" Spoke with ").add(other, "name_single_mid", "Single names (mid sentence)").add(" at the front desk about the bus pass.")
    if R.random() < 0.4:
        other = R.choice(WORD_NAMES) if R.random() < 0.5 else R.choice(FIRST)
        kind = "name_word_start" if other in WORD_NAMES else "name_single_start"
        grp = "Word names starting a sentence (Grace, Hope)" if other in WORD_NAMES else "Single names starting a sentence"
        n.add("\n").add(other, kind, grp).add(" from the youth program dropped off the forms.")
    if R.random() < 0.12:
        n.add("\nInterpreter confirmed the spelling: ").add(R.choice(NONLATIN), "name_nonlatin", "Names in non-Latin script").add(".")
    if R.random() < 0.25:
        n.add("\n").add(R.choice(DESCRIPTIONS), "description", "Descriptions that identify someone")
    if R.random() < 0.1:
        n.add(" Card on file ").add(R.choice(["4111 1111 1111 1111", "5555 5555 5555 4444"]), "credit_card", "ID and health numbers").add(".")
    return n


def main():
    notes = [build(i + 1).json() for i in range(200)]
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        for n in notes:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
    kinds = {}
    for n in notes:
        for e in n["entities"]:
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print(len(notes), "notes,", sum(kinds.values()), "personal details")
    for k, v in sorted(kinds.items(), key=lambda x: -x[1]):
        print(f"  {k:26s} {v}")


if __name__ == "__main__":
    main()
