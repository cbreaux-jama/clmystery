#!/usr/bin/env python3
"""Build the alternate cases on top of the original shared mystery dataset."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict


ROOT = Path(__file__).resolve().parents[1]
MYSTERY = ROOT / "mystery"


class Scenario(TypedDict):
    key: str
    title: str
    clues: tuple[str, ...]
    witnesses: tuple[tuple[str, str, str, int, str, bool], ...]
    witness_detail: str
    vehicle: tuple[str, str, str, str, str, str]
    decoy_vehicles: tuple[tuple[str, str, str, str], ...]
    suspect: tuple[str, str, str, int]
    decoys: tuple[str, ...]
    decoy_streets: tuple[str, ...]
    groups: tuple[str, ...]
    plate_hint: tuple[str, str]
    getaway: str


SCENARIOS: tuple[Scenario, ...] = (
    {
        "key": "gallery",
        "title": "Art Gallery",
        "clues": (
            "The gallery's jeweled compass disappeared during the 21:14 blackout.",
            "Camera footage shows a man at least six feet tall leaving the loading area.",
            "A wallet held membership cards for AAA, REI, and the Rotary Club.",
            "A woman named Avery, with copper braids and a New Zealand accent, spoke to the cafe barista.",
        ),
        "witnesses": (
            ("Avery Calder", "F", "Gallery_Quay", 317, "71824635", True),
            ("Avery Dupont", "M", "Juniper_Loop", 53, "18359042", False),
            ("Avery Yoon", "F", "Papermill_Road", 441, "94261708", False),
        ),
        "witness_detail": "copper braids and a New Zealand accent",
        "vehicle": ("Q7X4M32", "Volvo", "White", "Devin Merritt", "6'4\"", "203"),
        "decoy_vehicles": (
            ("Q7X1AB5", "Ewan Rusk", "5'8\"", "175"),
            ("Q7X3CD8", "Marta Corven", "5'6\"", "148"),
            ("Q7X9EF7", "Tobias Neel", "5'10\"", "187"),
        ),
        "suspect": ("Devin Merritt", "38", "Mercer_Crescent", 20),
        "decoys": ("Ewan Rusk", "Marta Corven", "Tobias Neel"),
        "decoy_streets": ("Rusk_Lane", "Corven_Court", "Neel_Terrace"),
        "groups": ("AAA", "REI", "Rotary_Club"),
        "plate_hint": ("Q7X", "2"),
        "getaway": "a white Volvo with a plate beginning Q7X and ending in 2",
    },
    {
        "key": "harbor",
        "title": "Harbor",
        "clues": (
            "The harbor pump was sabotaged shortly after the 03:20 shift change.",
            "A camera shows a man at least six feet tall near the pump controls.",
            "A discarded wallet contained cards for Costco, AAdvantage, and United MileagePlus.",
            "A man named Jordan, wearing silver earrings and speaking Portuguese, was seen on the pier.",
        ),
        "witnesses": (
            ("Jordan Bisset", "M", "Harbor_Walk", 271, "26518493", True),
            ("Jordan Medina", "F", "Saltwind_Terrace", 64, "89157206", False),
            ("Jordan Singh", "M", "Gullwatch_Avenue", 488, "43760918", False),
        ),
        "witness_detail": "silver earrings and a Portuguese accent",
        "vehicle": ("V8Z2D17", "Subaru", "Silver", "Kellan Duarte", "6'2\"", "196"),
        "decoy_vehicles": (
            ("V8Z1AB3", "Soren Vell", "5'9\"", "184"),
            ("V8Z5CD9", "Mara Quist", "5'5\"", "139"),
            ("V8Z7EF4", "Hugo Renn", "5'11\"", "201"),
        ),
        "suspect": ("Kellan Duarte", "41", "Duarte_Street", 20),
        "decoys": ("Soren Vell", "Mara Quist", "Hugo Renn"),
        "decoy_streets": ("Vell_Street", "Quist_Avenue", "Renn_Place"),
        "groups": ("Costco", "AAdvantage", "United_MileagePlus"),
        "plate_hint": ("V8Z", "7"),
        "getaway": "a silver Subaru with a plate beginning V8Z and ending in 7",
    },
    {
        "key": "archive",
        "title": "City Archive",
        "clues": (
            "A signed ledger vanished from the city archive after the 18:06 closing bell.",
            "A camera shows a man at least six feet tall leaving the restricted reading room.",
            "A wallet contained cards for Delta SkyMiles, the TCSU Alumni Association, and the Terminal City Library.",
            "A woman named Morgan, wearing a blue scarf and speaking Tagalog, was waiting outside.",
        ),
        "witnesses": (
            ("Morgan Noll", "F", "Archive_Row", 133, "76429031", True),
            ("Morgan Haddad", "F", "Ledger_Lane", 88, "31847562", False),
            ("Morgan Valdez", "M", "Catalog_Court", 399, "59204718", False),
        ),
        "witness_detail": "a blue scarf and a Tagalog accent",
        "vehicle": ("Z8J4R21", "Lexus", "Red", "Malik Ainsley", "6'1\"", "188"),
        "decoy_vehicles": (
            ("Z8J1AB7", "Lennox Grier", "5'7\"", "179"),
            ("Z8J3CD8", "Farah Dace", "5'4\"", "132"),
            ("Z8J9EF5", "Ivo Kest", "5'10\"", "191"),
        ),
        "suspect": ("Malik Ainsley", "36", "Ainsley_Alley", 20),
        "decoys": ("Lennox Grier", "Farah Dace", "Ivo Kest"),
        "decoy_streets": ("Grier_Road", "Dace_Lane", "Kest_Court"),
        "groups": ("Delta_SkyMiles", "TCSU_Alumni_Association", "Terminal_City_Library"),
        "plate_hint": ("Z8J", "1"),
        "getaway": "a red Lexus with a plate beginning Z8J and ending in 1",
    },
    {
        "key": "greenhouse",
        "title": "Greenhouse",
        "clues": (
            "A rare orchid was taken from the greenhouse during the 05:12 watering round.",
            "A camera shows a man at least six feet tall leaving through the service gate.",
            "A wallet held cards for Fitness Galaxy, the Museum of Bash History, and AAA.",
            "A man named Casey, wearing a yellow raincoat and speaking Korean, reported seeing a car.",
        ),
        "witnesses": (
            ("Casey Kessler", "M", "Glasshouse_Lane", 412, "14782936", True),
            ("Casey Morrow", "M", "Fernbank_Way", 103, "83640157", False),
            ("Casey Anwar", "F", "Orchid_Road", 267, "52169304", False),
        ),
        "witness_detail": "a yellow raincoat and a Korean accent",
        "vehicle": ("T9W5C84", "Honda", "Black", "Rowan Ivers", "6'3\"", "199"),
        "decoy_vehicles": (
            ("T9W1AB2", "Caspian Roh", "5'8\"", "166"),
            ("T9W3CD6", "Nadia Venn", "5'3\"", "130"),
            ("T9W7EF9", "Oren Trask", "5'11\"", "193"),
        ),
        "suspect": ("Rowan Ivers", "44", "Ivers_Road", 20),
        "decoys": ("Caspian Roh", "Nadia Venn", "Oren Trask"),
        "decoy_streets": ("Roh_Walk", "Venn_Terrace", "Trask_Drive"),
        "groups": ("Fitness_Galaxy", "Museum_of_Bash_History", "AAA"),
        "plate_hint": ("T9W", "4"),
        "getaway": "a black Honda with a plate beginning T9W and ending in 4",
    },
)

NOISE_NOTES = (
    "routine foot patrol completed without incident",
    "street lighting inspected and found operational",
    "delivery entrance secured after closing",
    "no property loss reported by the evening staff",
    "a loose sign was referred to the maintenance crew",
    "the west corridor was clear during the scheduled check",
    "a noise complaint was resolved before officers arrived",
)


def append_unique_lines(path: Path, lines: list[str]) -> None:
    original = path.read_text(encoding="utf-8")
    existing = set(original.splitlines())
    additions = [line for line in lines if line not in existing]
    if additions:
        separator = "" if not original or original.endswith("\n") else "\n"
        path.write_text(
            original + separator + "\n".join(additions) + "\n",
            encoding="utf-8",
        )


def append_unique_records(path: Path, records: list[str]) -> None:
    original = path.read_text(encoding="utf-8")
    additions = [record for record in records if record not in original]
    if additions:
        separator = "" if not original or original.endswith("\n\n") else "\n"
        path.write_text(
            original + separator + "\n".join(additions),
            encoding="utf-8",
        )


def replace_people_rows(path: Path, generated_names: set[str], rows: list[str]) -> None:
    original_rows = path.read_text(encoding="utf-8").splitlines()
    retained_rows = [
        row
        for row in original_rows
        if not (row.partition("\t")[0] in generated_names and "\t" in row)
    ]
    path.write_text("\n".join((*retained_rows, *rows)) + "\n", encoding="utf-8")


def person_address(row: str) -> tuple[str, int] | None:
    columns = row.split("\t")
    if len(columns) < 4:
        return None
    address = columns[3].rsplit(", line ", 1)
    if len(address) != 2 or not address[1].isdigit():
        return None
    return address[0].replace(" ", "_"), int(address[1])


def ensure_search_streets() -> None:
    search_names = (
        "Annabel",
        *(scenario["witnesses"][0][0].split()[0] for scenario in SCENARIOS),
    )
    people_rows = (MYSTERY / "people").read_text(encoding="utf-8").splitlines()
    search_streets: set[str] = set()
    for row in people_rows:
        if not any(name in row for name in search_names):
            continue
        address = person_address(row)
        if address is None:
            raise ValueError(f"Could not parse a clue-search result address: {row}")
        search_streets.add(address[0])

    required_lines = {street: 0 for street in search_streets}
    for row in people_rows:
        address = person_address(row)
        if address is not None and address[0] in required_lines:
            required_lines[address[0]] = max(required_lines[address[0]], address[1])

    for street, last_line in required_lines.items():
        path = MYSTERY / "streets" / street
        exists = path.exists()
        lines = path.read_text(encoding="utf-8").splitlines() if exists else []
        original_length = len(lines)
        target_length = max(last_line, 500 if not exists else 0)
        while len(lines) < target_length:
            line_number = len(lines) + 1
            lines.append(
                f"Patrol note {line_number:03}: "
                f"{NOISE_NOTES[line_number % len(NOISE_NOTES)]}."
            )
        if not exists or len(lines) > original_length:
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_crimescene(scenario: Scenario, scenario_index: int) -> str:
    clues = scenario["clues"]
    clue_reports = {317: clues[0], 1427: clues[1], 2389: clues[2], 2603: clues[3]}
    rows = [
        "***************",
        f"Terminal City {scenario['title']} Incident Report",
        "***************",
        "",
    ]
    for report_number in range(1, 2701):
        body = clue_reports.get(
            report_number,
            f"Officer notes: {NOISE_NOTES[report_number % len(NOISE_NOTES)]}.",
        )
        report_id = 910000000000 + scenario_index * 10000 + report_number
        rows.extend(
            (
                "*******",
                f"Crime Scene Report #{report_id}",
                "********",
                f"CLUE: {body}" if report_number in clue_reports else body,
                "",
            )
        )
    return "\n".join(rows)


def make_street(line_number: int | None, interview_id: str | None) -> str:
    rows = [
        f"Patrol note {index:03}: {NOISE_NOTES[index % len(NOISE_NOTES)]}."
        for index in range(1, 501)
    ]
    if line_number is not None and interview_id is not None:
        rows[line_number - 1] = f"SEE INTERVIEW #{interview_id}"
    return "\n".join(rows) + "\n"


def make_interviews(scenario: Scenario) -> dict[str, str]:
    witness_name = scenario["witnesses"][0][0]
    true_interview = (
        f"Interviewed {witness_name}. The witness confirmed {scenario['witness_detail']}. "
        f"They saw {scenario['getaway']} leave just after the incident."
    )
    statements = {
        scenario["witnesses"][0][4]: true_interview,
        scenario["witnesses"][1][4]: (
            f"Interviewed {scenario['witnesses'][1][0]}. The witness was away from the site "
            "before the incident and did not see a vehicle."
        ),
        scenario["witnesses"][2][4]: (
            f"Interviewed {scenario['witnesses'][2][0]}. The witness left before the incident "
            "and could not identify anyone or any vehicle."
        ),
    }
    return {
        f"interview-{interview_id}": f"{statement}\n"
        for interview_id, statement in statements.items()
    }


def main() -> None:
    person_rows: list[str] = []
    generated_names: set[str] = set()
    vehicle_records: list[str] = []
    membership_rows: dict[str, list[str]] = {}
    street_records: dict[str, tuple[int | None, str | None]] = {}

    for scenario_index, scenario in enumerate(SCENARIOS):
        for witness in scenario["witnesses"]:
            name, gender, street, line_number, interview_id = (
                witness[0],
                witness[1],
                witness[2],
                witness[3],
                witness[4],
            )
            age = 24 + line_number % 23
            person_rows.append(
                f"{name}\t{gender}\t{age}\t{street.replace('_', ' ')}, line {line_number}"
            )
            generated_names.add(name)
            street_records[street] = (line_number, interview_id)

        suspect_name, suspect_age, suspect_street, suspect_line = scenario["suspect"]
        person_rows.append(
            f"{suspect_name}\tM\t{suspect_age}\t{suspect_street.replace('_', ' ')}, line {suspect_line}"
        )
        generated_names.add(suspect_name)
        street_records[suspect_street] = (suspect_line, None)

        target_plate, make, color, target_owner, target_height, target_weight = scenario["vehicle"]
        for decoy_index, (plate, owner, height, weight) in enumerate(scenario["decoy_vehicles"]):
            owner_street = scenario["decoy_streets"][decoy_index]
            person_rows.append(f"{owner}\tM\t35\t{owner_street.replace('_', ' ')}, line 20")
            generated_names.add(owner)
            street_records[owner_street] = (20, None)
            vehicle_records.append(
                "\n".join(
                    (
                        f"License Plate {plate}",
                        f"Make: {make}",
                        f"Color: {color}",
                        f"Owner: {owner}",
                        f"Height: {height}",
                        f"Weight: {weight} lbs",
                        "",
                    )
                )
            )
        vehicle_records.append(
            "\n".join(
                (
                    f"License Plate {target_plate}",
                    f"Make: {make}",
                    f"Color: {color}",
                    f"Owner: {target_owner}",
                    f"Height: {target_height}",
                    f"Weight: {target_weight} lbs",
                    "",
                )
            )
        )

        groups = scenario["groups"]
        suspect = scenario["vehicle"][3]
        plate_prefix, plate_suffix = scenario["plate_hint"]
        if not scenario["vehicle"][0].startswith(plate_prefix) or not scenario["vehicle"][0].endswith(plate_suffix):
            raise ValueError(f"Vehicle plate does not match the clue fragments for {scenario['key']}.")
        for group in groups:
            membership_rows.setdefault(group, []).append(suspect)
        for decoy_index, decoy_name in enumerate(scenario["decoys"]):
            for group_index, group in enumerate(groups):
                if group_index != decoy_index:
                    membership_rows.setdefault(group, []).append(decoy_name)

        scenario_dir = ROOT / "case_files" / scenario["key"] / "mystery"
        scene_path = scenario_dir / "crimescene"
        scene_path.write_text(make_crimescene(scenario, scenario_index), encoding="utf-8")
        for interview_name, content in make_interviews(scenario).items():
            (MYSTERY / "interviews" / interview_name).write_text(content, encoding="utf-8")

    replace_people_rows(MYSTERY / "people", generated_names, person_rows)
    append_unique_records(MYSTERY / "vehicles", vehicle_records)
    ensure_search_streets()
    for street_name, (line_number, interview_id) in street_records.items():
        street_path = MYSTERY / "streets" / street_name
        street_path.write_text(make_street(line_number, interview_id), encoding="utf-8")
    for group, names in membership_rows.items():
        append_unique_lines(MYSTERY / "memberships" / group, names)

    print("Generated alternate crime scenes and shared investigation records.")


if __name__ == "__main__":
    main()
