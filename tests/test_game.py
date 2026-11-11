import tempfile
import unittest
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

import game


class GameTests(unittest.TestCase):
    def test_five_cases_have_distinct_answers(self):
        self.assertEqual(len(game.CASES), 5)
        answers = {case.answer.casefold() for case in game.CASES.values()}
        self.assertEqual(len(answers), 5)

    def test_case_scenes_have_distinct_clue_trails(self):
        clue_trails = {
            game.Game(case).execute_line('grep "CLUE" crimescene')
            for case in game.CASES.values()
        }
        self.assertEqual(len(clue_trails), len(game.CASES))

    def test_clue_name_results_have_existing_streets_and_lines(self):
        player = game.Game(game.CASES["archive"])
        for name in ("Annabel", "Avery", "Jordan", "Morgan", "Casey"):
            with self.subTest(name=name):
                matches = player.execute_line(f'grep "{name}" people').splitlines()
                self.assertTrue(matches)
                for row in matches:
                    columns = row.split("\t")
                    self.assertEqual(len(columns), 4, row)
                    address, line_number = columns[3].rsplit(", line ", 1)
                    street = address.replace(" ", "_")
                    path = player.resolve_path(f"streets/{street}")
                    lines = player.read_case_file(path).splitlines()
                    self.assertGreaterEqual(len(lines), int(line_number), row)

    def test_case_assignment_is_saved_and_reused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            assignment_file = Path(temp_dir) / ".case-assignment"
            with patch.object(game, "ASSIGNMENT_FILE", assignment_file):
                with patch.object(game.secrets, "choice", return_value="gallery") as choose:
                    self.assertEqual(game.assign_case(), "gallery")
                    self.assertEqual(game.assign_case(), "gallery")
                    choose.assert_called_once()

    def test_new_case_assignment_differs_from_previous(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            assignment_file = Path(temp_dir) / ".case-assignment"
            assignment_file.write_text("gallery\n", encoding="utf-8")
            with patch.object(game, "ASSIGNMENT_FILE", assignment_file):
                with patch.object(game.secrets, "choice", side_effect=lambda choices: choices[0]):
                    assigned = game.assign_case(new_case=True)
            self.assertNotEqual(assigned, "gallery")

    def test_original_answer_check_uses_existing_encoded_hashes(self):
        player = game.Game(game.CASES["original"])
        self.assertIn("CORRECT", player.check(["Jeremy", "Bowers"]))

    def test_alt_case_commands_find_the_answer(self):
        investigations = {
            "gallery": ("Avery", "Avery Calder", "Gallery_Quay", 317, "71824635", "Q7X", "AAA REI Rotary_Club", ("Avery Calder", "Avery Dupont", "Avery Yoon")),
            "harbor": ("Jordan", "Jordan Bisset", "Harbor_Walk", 271, "26518493", "V8Z", "Costco AAdvantage United_MileagePlus", ("Jordan Bisset", "Jordan Medina", "Jordan Singh")),
            "archive": ("Morgan", "Morgan Noll", "Archive_Row", 133, "76429031", "Z8J", "Delta_SkyMiles TCSU_Alumni_Association Terminal_City_Library", ("Morgan Noll", "Morgan Haddad", "Morgan Valdez")),
            "greenhouse": ("Casey", "Casey Kessler", "Glasshouse_Lane", 412, "14782936", "T9W", "Fitness_Galaxy Museum_of_Bash_History AAA", ("Casey Kessler", "Casey Morrow", "Casey Anwar")),
        }
        for key, (
            first_name,
            witness,
            street,
            line,
            interview_id,
            plate_prefix,
            groups,
            candidate_names,
        ) in investigations.items():
            with self.subTest(case=key):
                player = game.Game(game.CASES[key])
                clues = player.execute_line('grep "CLUE" crimescene')
                self.assertIn(first_name, clues)
                witness_rows = [
                    row
                    for row in player.execute_line(f'grep "{first_name}" people').splitlines()
                    if row.partition("\t")[0] in candidate_names
                ]
                self.assertIn(witness, "\n".join(witness_rows))
                self.assertEqual(len(witness_rows), 3)
                target_gender = next(
                    row.split("\t")[1]
                    for row in witness_rows
                    if row.partition("\t")[0] == witness
                )
                gender_word = "woman" if target_gender == "F" else "man"
                self.assertIn(f"{gender_word} named {first_name}", clues)
                self.assertEqual(
                    sum(row.split("\t")[1] == target_gender for row in witness_rows),
                    2,
                )
                witness_streets = {
                    row.split("\t")[3].rsplit(", line", 1)[0] for row in witness_rows
                }
                self.assertEqual(len(witness_streets), 3)
                self.assertEqual({row.split("\t")[1] for row in witness_rows}, {"F", "M"})
                candidate_interviews = []
                for row in witness_rows:
                    name, _, _, address = row.split("\t")
                    candidate_street, candidate_line = address.rsplit(", line ", 1)
                    reference = player.execute_line(
                        f"head -n {candidate_line} streets/{candidate_street.replace(' ', '_')} | tail -n 1"
                    )
                    self.assertTrue(reference.startswith("SEE INTERVIEW #"))
                    candidate_id = reference.removeprefix("SEE INTERVIEW #")
                    candidate_interviews.append(int(candidate_id))
                    interview_record = player.execute_line(
                        f"cat interviews/interview-{candidate_id}"
                    )
                    self.assertIn(name, interview_record)
                self.assertEqual(len(set(candidate_interviews)), 3)
                self.assertGreater(
                    max(candidate_interviews) - min(candidate_interviews),
                    10_000_000,
                )
                street_line = player.execute_line(
                    f"head -n {line} streets/{street} | tail -n 1"
                )
                self.assertEqual(street_line, f"SEE INTERVIEW #{interview_id}")
                interview = player.execute_line(f"cat interviews/interview-{interview_id}")
                self.assertIn(plate_prefix, interview)
                vehicle = player.execute_line(f'grep -A 5 "{plate_prefix}" vehicles')
                self.assertIn(game.CASES[key].answer, vehicle)
                self.assertIn("6'", vehicle)
                member_count = player.execute_line(
                    f'cat memberships/{groups.replace(" ", " memberships/")} '
                    f'| grep "{game.CASES[key].answer}" | wc -l'
                )
                self.assertEqual(member_count.strip(), "3")
                self.assertIn("CORRECT", player.check([game.CASES[key].answer]))
                self.assertGreater(int(player.execute_line("wc -l vehicles").split()[0]), 35_000)

    def test_original_clue_search_and_pipeline(self):
        player = game.Game(game.CASES["original"])
        clues = player.execute_line('grep "CLUE" crimescene')
        self.assertIn("tall male", clues)
        interview = player.execute_line("head -n 173 streets/Mattapan_Street | tail -n 1")
        self.assertIn("interview", interview.casefold())

    def test_grep_context_options_work_after_files(self):
        player = game.Game(game.CASES["gallery"])
        after = player.execute_line('grep "T9W.*4" vehicles -A2')
        self.assertEqual(
            after.splitlines(),
            ["License Plate T9W5C84", "Make: Honda", "Color: Black"],
        )
        separated_after = player.execute_line('grep "T9W.*4" vehicles -A 2')
        self.assertEqual(separated_after, after)

        before = player.execute_line('grep "T9W.*4" vehicles -B2')
        self.assertIn("Weight:", before)
        self.assertTrue(before.endswith("License Plate T9W5C84"))

    def test_all_case_answers_validate(self):
        for case in game.CASES.values():
            with self.subTest(case=case.key):
                self.assertIn("CORRECT", game.Game(case).check([case.answer]))

    def test_pipe_and_hint_commands(self):
        player = game.Game(game.CASES["harbor"])
        self.assertIn("CLUE", player.execute_line('cat crimescene | grep "CLUE" | head -n 1'))
        self.assertIn("Hint 1", player.execute_line("hint"))

    def test_awk_prints_fields_and_filters_lines(self):
        player = game.Game(game.CASES["gallery"])
        people = player.execute_line(r"""awk -F '\t' '{print $1, $2}' people""")
        self.assertIn("Avery Calder F", people.splitlines())
        self.assertIn("Avery Dupont M", people.splitlines())

        filtered = player.execute_line(r"""awk '/Avery/ {print $1}' people""")
        self.assertEqual(filtered.splitlines(), ["Avery", "Avery", "Avery"])

        piped = player.execute_line(
            r"""grep "CLUE" crimescene | awk '/Avery/ {print $0}' | head -n 1"""
        )
        self.assertIn("Avery", piped)

        harbor = game.Game(game.CASES["harbor"])
        male_jordans = harbor.execute_line(
            r"""grep Jordan people | awk '{if ($3 == "M") print $0}'"""
        )
        self.assertIn("Jordan Bisset", male_jordans)
        self.assertIn("Jordan Singh", male_jordans)
        self.assertNotIn("Jordan Medina", male_jordans)

    def test_cheatsheet_command_shows_reference_and_topics(self):
        player = game.Game(game.CASES["original"])
        reference = player.execute_line("cheatsheet")
        self.assertIn("NAVIGATION", reference)
        self.assertIn("SEARCHING", reference)
        self.assertIn("PIPES", reference)
        self.assertIn("awk -F", reference)
        self.assertIn('if ($3 == "M")', reference)
        navigation = player.execute_line("cheatsheet navigation").splitlines()
        self.assertEqual(navigation[1], "  pwd")
        self.assertEqual(navigation[2], "    Show where you are.")
        with self.assertRaises(ValueError):
            player.execute_line("cheatsheet missing")

    def test_tab_completion_suggests_commands_and_case_paths(self):
        player = game.Game(game.CASES["original"])
        self.assertIn("cheatsheet", player.completion_candidates("cheat", "cheat", 0))
        self.assertIn("awk", player.completion_candidates("aw", "aw", 0))
        self.assertIn("crimescene", player.completion_candidates("cat ", "", 4))
        self.assertIn("crimescene", player.completion_candidates("cat crim", "crim", 4))
        self.assertIn("streets/", player.completion_candidates("cd ", "", 3))

        awk_prefix = "awk '{print $1}' "
        self.assertIn(
            "people",
            player.completion_candidates(awk_prefix + "peo", "peo", len(awk_prefix)),
        )

        gallery = game.Game(game.CASES["gallery"])
        self.assertIn("vehicles", gallery.completion_candidates('grep "Q7X" ', "", 11))

    def test_tab_completion_is_bound_to_readline(self):
        player = game.Game(game.CASES["original"])
        if player.enable_tab_completion():
            self.assertIsNotNone(player.readline_module)
            self.assertEqual(player.readline_module.get_completer(), player.readline_complete)

    def test_terminal_feedback_and_grep_matches_can_be_colored(self):
        player = game.Game(game.CASES["gallery"], color_enabled=True)
        self.assertIn("\033[1;33m", player.execute_line("hint"))
        self.assertIn("\033[1;32m", player.execute_line("check Devin Merritt"))
        self.assertIn("\033[1;31m", player.execute_line("check wrong"))
        matches = player.execute_line('grep "Q7X" vehicles')
        self.assertIn("\033[1;31mQ7X\033[0m", matches)

    def test_correct_check_shows_time_and_successful_commands(self):
        player = game.Game(game.CASES["gallery"])
        player.execute_line("pwd")
        player.execute_line('grep "CLUE" crimescene')
        with self.assertRaises(ValueError):
            player.execute_line("ll")
        player.execute_line("check wrong")

        with patch("game.time.monotonic", return_value=player.started_at + 60):
            result = player.execute_line("check Devin Merritt")

        self.assertIn("CORRECT! GREAT WORK, GUMSHOE.", result)
        self.assertIn("  1. pwd", result)
        self.assertIn('  2. grep "CLUE" crimescene', result)
        self.assertIn("  3. check Devin Merritt", result)
        self.assertNotIn("ll", result)
        self.assertNotIn("check wrong", result)
        self.assertIn("Time to Complete: 1.00 minutes", result)

    def test_game_starts_in_an_interactive_prompt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            assignment_file = Path(temp_dir) / ".case-assignment"
            output = StringIO()
            with patch.object(game, "ASSIGNMENT_FILE", assignment_file):
                with patch.object(game.secrets, "choice", return_value="gallery"):
                    with patch("builtins.input", side_effect=["pwd", "check Devin Merritt", "quit"]):
                        with redirect_stdout(output):
                            self.assertEqual(game.main(["--color", "always"]), 0)
            self.assertIn("THE COMMAND LINE MURDERS", output.getvalue())
            self.assertIn(".OOOOOOOOOOOOOOO", output.getvalue())
            self.assertIn("\033[1;36mTHE COMMAND LINE MURDERS\033[0m", output.getvalue())
            self.assertIn(
                "\033[1;36mhelp\033[0m to see the available commands",
                output.getvalue(),
            )
            self.assertIn("\033[1;36mcrimescene\033[0m", output.getvalue())
            self.assertIn("\033[1;36mcheatsheet\033[0m", output.getvalue())
            self.assertIn("\033[1;33mhint\033[0m", output.getvalue())
            self.assertIn("\033[1;36mhelp\033[0m", output.getvalue())
            self.assertNotIn("`crimescene`", output.getvalue())
            self.assertNotIn("Color key:", output.getvalue())
            self.assertNotIn("security boundary", output.getvalue())
            self.assertIn("CORRECT", output.getvalue())
            self.assertIn("Commands used:", output.getvalue())
            self.assertIn("  1. pwd", output.getvalue())
            self.assertIn("  2. check Devin Merritt", output.getvalue())
            self.assertIn("Time to Complete:", output.getvalue())

            title = "\033[1;36mTHE COMMAND LINE MURDERS\033[0m"
            art = (game.ROOT / "instructions").read_text(encoding="utf-8").partition(
                "\n\nThere's been a crime in Terminal City, and the police need your help.\n\n"
            )[0]
            self.assertIn(f"{art}\n{title}\n\n", output.getvalue())

    def test_game_color_option_forces_colors_without_a_tty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            assignment_file = Path(temp_dir) / ".case-assignment"
            output = StringIO()
            with patch.object(game, "ASSIGNMENT_FILE", assignment_file):
                with patch.object(game.secrets, "choice", return_value="gallery"):
                    with patch("builtins.input", side_effect=["quit"]):
                        with redirect_stdout(output):
                            self.assertEqual(game.main(["--color", "always"]), 0)
            self.assertIn("\033[1;33mhint\033[0m", output.getvalue())
            self.assertIn("\033[1;36mTHE COMMAND LINE MURDERS\033[0m", output.getvalue())

    def test_case_commands_cannot_read_outside_the_assigned_files(self):
        player = game.Game(game.CASES["gallery"])
        with self.assertRaises(ValueError):
            player.execute_line("cat ../README.md")


if __name__ == "__main__":
    unittest.main()
