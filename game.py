#!/usr/bin/env python3
"""Play The Command Line Murders in a guided, shell-like terminal."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import secrets
import shlex
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ASSIGNMENT_FILE = ROOT / ".case-assignment"

ORIGINAL_HINTS = (
    "Try poking around with `head -n 20 people` to see what the people file contains.",
    'Search the crime scene for marked clues: `grep "CLUE" crimescene`.',
    "Look for the witness in `people`, then use their street and line number to find the interview.",
    'Search for Annabel with `grep "Annabel" people`. Use the witness details to choose the right person.',
    "Read one street line with `head -n 173 streets/Mattapan_Street | tail -n 1`.",
    "Use `grep` on vehicles to find a plate or car description. Inspect several lines around a match.",
    'For example: `grep -A 5 "L337" vehicles` prints the matching line and five lines after it.',
    "Combine membership files and search them for a suspect, for example: `cat memberships/AAA memberships/Delta_SkyMiles | grep 'John Smith'`.",
)


@dataclass(frozen=True)
class Case:
    key: str
    title: str
    root: Path
    answer: str
    hints: tuple[str, ...]
    crimescene_override: Path | None = None


CASES = {
    "original": Case(
        "original",
        "The Command Line Murders",
        ROOT / "mystery",
        "Jeremy Bowers",
        ORIGINAL_HINTS,
    ),
    "gallery": Case(
        "gallery",
        "The Gallery Job",
        ROOT / "mystery",
        "Devin Merritt",
        (
            'Search the reports with `grep "CLUE" crimescene` and note the witness and membership clues.',
            'Search `people` for the name Avery; there are several possible witnesses.',
            "Use each candidate's address to read the matching line in `streets`.",
            "Follow each `SEE INTERVIEW` reference. Only one witness describes the getaway car.",
            'Search the vehicle records with `grep -A 5 "Q7X" vehicles`.',
            "Several cars share that prefix. Use the plate ending and vehicle details to identify the right one.",
            'Check the owner in `people`, then search the three membership files named in the crime-scene report.',
            'Combine the three membership files and count the suspect with `cat FILES | grep "NAME" | wc -l`.',
        ),
        ROOT / "case_files" / "gallery" / "mystery" / "crimescene",
    ),
    "harbor": Case(
        "harbor",
        "The Harbor Sabotage",
        ROOT / "mystery",
        "Kellan Duarte",
        (
            'Search the reports with `grep "CLUE" crimescene` and note the witness and membership clues.',
            'Search `people` for the name Jordan; there are several possible witnesses.',
            "Use each candidate's address to read the matching line in `streets`.",
            "Follow each `SEE INTERVIEW` reference. Only one witness identifies the harbor vehicle.",
            'Search the vehicle records with `grep -A 5 "V8Z" vehicles`.',
            "Several cars share that prefix. Use the plate ending and vehicle details to identify the right one.",
            'Check the owner in `people`, then search the three membership files named in the crime-scene report.',
            'Combine the three membership files and count the suspect with `cat FILES | grep "NAME" | wc -l`.',
        ),
        ROOT / "case_files" / "harbor" / "mystery" / "crimescene",
    ),
    "archive": Case(
        "archive",
        "The Missing Ledger",
        ROOT / "mystery",
        "Malik Ainsley",
        (
            'Search the reports with `grep "CLUE" crimescene` and note the witness and membership clues.',
            'Search `people` for the name Morgan; there are several possible witnesses.',
            "Use each candidate's address to read the matching line in `streets`.",
            "Follow each `SEE INTERVIEW` reference. Only one witness describes the archive vehicle.",
            'Search the vehicle records with `grep -A 5 "Z8J" vehicles`.',
            "Several cars share that prefix. Use the plate ending and vehicle details to identify the right one.",
            'Check the owner in `people`, then search the three membership files named in the crime-scene report.',
            'Combine the three membership files and count the suspect with `cat FILES | grep "NAME" | wc -l`.',
        ),
        ROOT / "case_files" / "archive" / "mystery" / "crimescene",
    ),
    "greenhouse": Case(
        "greenhouse",
        "The Greenhouse Incident",
        ROOT / "mystery",
        "Rowan Ivers",
        (
            'Search the reports with `grep "CLUE" crimescene` and note the witness and membership clues.',
            'Search `people` for the name Casey; there are several possible witnesses.',
            "Use each candidate's address to read the matching line in `streets`.",
            "Follow each `SEE INTERVIEW` reference. Only one witness identifies the greenhouse vehicle.",
            'Search the vehicle records with `grep -A 5 "T9W" vehicles`.',
            "Several cars share that prefix. Use the plate ending and vehicle details to identify the right one.",
            'Check the owner in `people`, then search the three membership files named in the crime-scene report.',
            'Combine the three membership files and count the suspect with `cat FILES | grep "NAME" | wc -l`.',
        ),
        ROOT / "case_files" / "greenhouse" / "mystery" / "crimescene",
    ),
}

WELCOME_MESSAGES = (
    "A new file is on your desk. Start with the crime scene report.",
    "The department needs your help. Begin by examining the crime scene.",
    "Your shift starts now. Gather the marked clues before drawing a conclusion.",
    "A case is waiting. Use the records to work out who is responsible.",
    "The evidence room is open. Start at the crime scene and follow the trail.",
)

HELP_TEXT = """Available commands:
  pwd                         Show your current location
  ls [path]                   List files and directories
  cd [directory]              Change directories
  cat FILE [FILE ...]         Print file contents
  grep [OPTIONS] PATTERN FILE Search for text or a regular expression
      Options: -i -w -n -c -l -r -A N -B N -C N (before or after files)
  awk [-F SEP] PROGRAM [FILE ...]
                              Print selected fields, optionally matching a pattern or test
  head [-n N] FILE             Print the first lines
  tail [-n N] FILE             Print the last lines
  wc [-l] FILE                 Count lines
  COMMAND | COMMAND            Pipe output to another command
  cheatsheet [topic]           Show the command reference
  hint [number]                Show a hint; without a number, show the next one
  check NAME                   Check your answer
  solution                     Reveal the answer
  help                         Show this help
  quit                         Leave the game

Commands only read the assigned case files. File-writing redirection and
arbitrary operating-system commands are not available in the game prompt.
When supported, colors highlight hints, answer results, and grep matches."""

CHEATSHEET = {
    "navigation": """NAVIGATION
  pwd
    Show where you are.
  ls
    List files and folders.
  cd streets
    Enter a folder.
  cd ..
    Go up one folder.
  cd /
    Return to the case's top-level folder.

Paths without a leading slash are relative to your current folder.
Paths beginning with / start at the case's top-level folder.
Press Tab to complete game commands and file paths.""",
    "files": """VIEWING FILES
  cat crimescene
    Print a file.
  head -n 20 people
    Print the first 20 lines.
  tail -n 10 people
    Print the last 10 lines.
  tail -n +2 people
    Print from line 2 onward.
  head -n 20 people | tail -n 1
    Print line 20.
  wc -l people
    Count the lines in a file.""",
    "search": """SEARCHING
  grep "CLUE" crimescene
    Find lines containing CLUE.
  grep -i "annabel" people
    Ignore uppercase/lowercase differences.
  grep -w "Annabel" people
    Match a whole word.
  grep -n "Annabel" people
    Include matching line numbers.
  grep -A 2 "Annabel" people
    Include two lines after each match.
  grep "Annabel" people -A2
    Context options may follow the file; the number can be attached.
  grep -B 2 "Annabel" people
    Include two lines before each match.
  grep -C 2 "Annabel" people
    Include two lines before and after each match.
  grep -c "Annabel" people
    Count matching lines.

Search patterns use regular expressions. In a pattern, a period (.) matches
any single character.

  awk -F '\\t' '{print $1}' people
    Print the first tab-separated field.
  awk '/CLUE/ {print $0}' crimescene
    Print lines matching a regular expression.
  grep "Avery" people | awk -F '\\t' '{print $1, $2}'
    Print the name and gender fields for matching people.
  grep Jordan people | awk '{if ($3 == "M") print $0}'
    Print matching rows whose third whitespace-separated field is M.

The game supports awk print programs using $0, numbered fields, and $NF, with
optional regular-expression matches or simple field-equals-string conditions.""",
    "pipes": """PIPES
Use | to send one command's output into another command:
  head -n 173 streets/Mattapan_Street | tail -n 1
    Print line 173 of the street file.
  cat memberships/AAA memberships/Delta_SkyMiles | grep "Jeremy Bowers"
    Search several membership lists for a name.

You can chain commands, for example:
  grep "United States" addresses | grep "California" | head
    Keep lines matching both phrases, then print the first 10.

The game supports pipes but does not support saving output with > or >>.""",
}


class Game:
    def __init__(self, case: Case, *, color_enabled: bool | None = None) -> None:
        self.case = case
        self.root = case.root.resolve()
        self.cwd = Path(".")
        self.next_hint = 0
        self.running = True
        self.started_at = time.monotonic()
        self.successful_commands: list[str] = []
        self.color_enabled = (
            sys.stdout.isatty()
            and os.environ.get("TERM") != "dumb"
            and "NO_COLOR" not in os.environ
            if color_enabled is None
            else color_enabled
        )
        self.color_grep_matches = False
        self.readline_module = None
        self.completion_matches: list[str] = []
        if not self.root.is_dir():
            raise FileNotFoundError(f"Case data directory not found: {case.root}")
        if case.crimescene_override is not None and not case.crimescene_override.is_file():
            raise FileNotFoundError(f"Case crime scene not found: {case.crimescene_override}")

    def colorize(self, text: str, color_code: str) -> str:
        if not self.color_enabled:
            return text
        return f"\033[{color_code}m{text}\033[0m"

    def render_instructions(self, text: str) -> str:
        return re.sub(
            r"(?<!`)`([^`\n]+)`(?!`)",
            lambda match: self.colorize(match.group(1), "1;36"),
            text,
        )

    def virtual_pwd(self) -> str:
        relative = self.cwd.as_posix()
        return "/mystery" if relative == "." else f"/mystery/{relative}"

    def resolve_path(self, value: str, *, must_exist: bool = True) -> Path:
        path = Path(value)
        if path.is_absolute():
            candidate = self.root / str(path).lstrip("/")
        else:
            candidate = self.root / self.cwd / path
        candidate = candidate.resolve(strict=must_exist)
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("That path is outside the assigned case files.") from exc
        return candidate

    def expand_paths(self, values: list[str]) -> list[Path]:
        paths: list[Path] = []
        for value in values:
            if any(char in value for char in "*?["):
                base = self.resolve_path(value, must_exist=False)
                matches = sorted(base.parent.glob(base.name))
                paths.extend(match.resolve() for match in matches)
            else:
                paths.append(self.resolve_path(value))
        if not paths:
            raise FileNotFoundError("No matching files.")
        for path in paths:
            try:
                path.relative_to(self.root)
            except ValueError as exc:
                raise ValueError("That path is outside the assigned case files.") from exc
        return paths

    def read_paths(self, values: list[str]) -> str:
        if not values:
            raise ValueError("Please provide a file name.")
        contents = []
        for path in self.expand_paths(values):
            if not path.is_file():
                raise IsADirectoryError(f"Not a file: {path.name}")
            contents.append(self.read_case_file(path))
        return "".join(contents)

    def read_case_file(self, path: Path) -> str:
        if self.case.crimescene_override is not None and path == self.root / "crimescene":
            return self.case.crimescene_override.read_text(encoding="utf-8")
        return path.read_text(encoding="utf-8")

    def hint(self, args: list[str]) -> str:
        if args:
            if len(args) != 1 or not args[0].isdigit():
                raise ValueError("Usage: hint [number]")
            index = int(args[0]) - 1
            if index < 0 or index >= len(self.case.hints):
                raise ValueError(f"Choose a hint from 1 to {len(self.case.hints)}.")
        else:
            index = self.next_hint
            if index >= len(self.case.hints):
                return "No more hints are available."
            self.next_hint += 1
        return self.colorize(f"Hint {index + 1}: {self.case.hints[index]}", "1;33")

    def check(self, args: list[str]) -> str:
        if not args:
            raise ValueError("Usage: check NAME")
        guess = " ".join(args).strip()
        if self.case.key == "original":
            encoded = (ROOT / "encoded").read_text(encoding="utf-8")
            valid_hashes = {
                line.split()[0]
                for line in encoded.splitlines()
                if re.fullmatch(r"[0-9a-fA-F]{32}", line.split()[0] if line.split() else "")
            }
            candidate_hash = hashlib.md5(f"{guess}\n".encode("utf-8")).hexdigest()
            correct = candidate_hash in valid_hashes
        else:
            correct = guess.casefold() == self.case.answer.casefold()
        if correct:
            return self.colorize("CORRECT! GREAT WORK, GUMSHOE.", "1;32")
        return self.colorize("Sorry, that's not the right answer. Keep investigating or use `hint`.", "1;31")

    def session_summary(self) -> str:
        commands = "\n".join(
            f"  {index}. {command}"
            for index, command in enumerate(self.successful_commands, start=1)
        )
        elapsed_minutes = (time.monotonic() - self.started_at) / 60
        return (
            f"Commands used:\n{commands}\n\n"
            f"Time to Complete: {elapsed_minutes:.2f} minutes"
        )

    def solution(self, args: list[str]) -> str:
        if args:
            raise ValueError("Usage: solution")
        return self.colorize(f"The correct answer is {self.case.answer}.", "1;36")

    def cheatsheet(self, args: list[str]) -> str:
        if len(args) > 1:
            raise ValueError("Usage: cheatsheet [navigation|files|search|pipes]")
        if not args:
            return "\n\n".join(CHEATSHEET.values())
        topic = args[0].casefold()
        if topic not in CHEATSHEET:
            topics = ", ".join(CHEATSHEET)
            raise ValueError(f"Unknown topic: {args[0]}. Choose from: {topics}.")
        return CHEATSHEET[topic]

    def execute_command(self, args: list[str], stdin: str | None = None) -> str:
        if not args:
            raise ValueError("Enter a command. Type `help` to see available commands.")
        command, *args = args

        if command in ("help",):
            if args:
                raise ValueError("Usage: help")
            return HELP_TEXT
        if command == "hint":
            return self.hint(args)
        if command == "check":
            return self.check(args)
        if command == "solution":
            return self.solution(args)
        if command == "cheatsheet":
            return self.cheatsheet(args)
        if command in ("quit", "exit"):
            self.running = False
            return "Good work, Gumshoe. Goodbye."
        if command == "pwd":
            if args:
                raise ValueError("Usage: pwd")
            return self.virtual_pwd()
        if command == "cd":
            if len(args) > 1:
                raise ValueError("Usage: cd [directory]")
            target = args[0] if args else "/"
            path = self.resolve_path(target)
            if not path.is_dir():
                raise NotADirectoryError(f"Not a directory: {target}")
            self.cwd = path.relative_to(self.root)
            return ""
        if command == "ls":
            return self.command_ls(args)
        if command == "cat":
            if not args and stdin is not None:
                return stdin
            return self.read_paths(args)
        if command == "grep":
            return self.command_grep(args, stdin)
        if command == "awk":
            return self.command_awk(args, stdin)
        if command in ("head", "tail"):
            return self.command_lines(command, args, stdin)
        if command == "wc":
            return self.command_wc(args, stdin)
        raise ValueError(f"Command not available: {command}. Type `help` for the game commands.")

    def completion_candidates(self, line_buffer: str, text: str, word_start: int) -> list[str]:
        prefix = line_buffer[:word_start]
        lexer = shlex.shlex(prefix, posix=True, punctuation_chars="|")
        lexer.whitespace_split = True
        try:
            tokens = list(lexer)
        except ValueError:
            tokens = prefix.split()

        if "|" in tokens:
            pipe_index = len(tokens) - 1 - tokens[::-1].index("|")
            tokens = tokens[pipe_index + 1 :]

        commands = (
            "pwd", "ls", "cd", "cat", "grep", "awk", "head", "tail", "wc",
            "cheatsheet", "hint", "check", "solution", "help", "quit",
        )
        if not tokens:
            return [command for command in commands if command.startswith(text)]

        command = tokens[0]
        args = tokens[1:]
        if command == "cd":
            return self.path_completions(text, directories_only=True)
        if command in ("ls", "cat", "head", "tail", "wc"):
            return self.path_completions(text)
        if command == "awk":
            index = 0
            while index < len(args) and args[index].startswith("-"):
                if args[index] == "-F":
                    index += 2
                elif args[index].startswith("-F"):
                    index += 1
                else:
                    return []
            if index < len(args):
                return self.path_completions(text)
        if command == "grep":
            index = 0
            while index < len(args) and args[index].startswith("-"):
                if args[index] in ("-A", "-B", "-C"):
                    index += 2
                else:
                    index += 1
            if index < len(args):
                return self.path_completions(text)
        return []

    def path_completions(self, text: str, *, directories_only: bool = False) -> list[str]:
        if "/" in text:
            directory_text, name_prefix = text.rsplit("/", 1)
            directory_text = f"{directory_text}/" if directory_text else "/"
            try:
                directory = self.resolve_path(directory_text)
            except (OSError, ValueError):
                return []
            insert_prefix = f"{directory_text.rstrip('/')}/"
        else:
            name_prefix = text
            directory = self.root / self.cwd
            insert_prefix = ""
        if not directory.is_dir():
            return []

        matches = []
        for entry in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
            if not entry.name.startswith(name_prefix):
                continue
            if entry.name.startswith(".") and not name_prefix.startswith("."):
                continue
            try:
                entry.resolve().relative_to(self.root)
            except ValueError:
                continue
            if directories_only and not entry.is_dir():
                continue
            suffix = "/" if entry.is_dir() else ""
            matches.append(f"{insert_prefix}{entry.name}{suffix}")
        return matches

    def readline_complete(self, text: str, state: int) -> str | None:
        if self.readline_module is None:
            return None
        if state == 0:
            line_buffer = self.readline_module.get_line_buffer()
            word_start = self.readline_module.get_begidx()
            self.completion_matches = self.completion_candidates(line_buffer, text, word_start)
        if state < len(self.completion_matches):
            return self.completion_matches[state]
        return None

    def enable_tab_completion(self) -> bool:
        try:
            import readline
        except ImportError:
            return False
        self.readline_module = readline
        readline.set_completer(self.readline_complete)
        readline.set_completer_delims(" \t\n")
        readline.parse_and_bind("tab: complete")
        return True

    def command_ls(self, args: list[str]) -> str:
        long_format = False
        if args and args[0] == "-l":
            long_format = True
            args = args[1:]
        if len(args) > 1:
            raise ValueError("Usage: ls [-l] [path]")
        path = self.resolve_path(args[0]) if args else self.resolve_path(".")
        if path.is_file():
            entries = [path]
        elif path.is_dir():
            entries = sorted(path.iterdir(), key=lambda item: item.name.casefold())
        else:
            raise FileNotFoundError(f"No such file or directory: {args[0] if args else '.'}")
        if long_format:
            return "\n".join(f"{entry.stat().st_size:>8} {entry.name}{'/' if entry.is_dir() else ''}" for entry in entries)
        return "\n".join(f"{entry.name}{'/' if entry.is_dir() else ''}" for entry in entries)

    def command_grep(self, args: list[str], stdin: str | None) -> str:
        ignore_case = count_only = line_numbers = whole_word = list_files = recursive = False
        before = after = 0
        remaining: list[str] = []
        index = 0
        while index < len(args):
            option = args[index]
            if option in ("-A", "-B", "-C"):
                index += 1
                if index >= len(args) or not args[index].isdigit():
                    raise ValueError(f"{option} needs a number.")
                amount = int(args[index])
                if option in ("-A", "-C"):
                    after = amount
                if option in ("-B", "-C"):
                    before = amount
            elif (
                len(option) > 2
                and option[:2] in ("-A", "-B", "-C")
                and option[2:].isdigit()
            ):
                amount = int(option[2:])
                if option[:2] in ("-A", "-C"):
                    after = amount
                if option[:2] in ("-B", "-C"):
                    before = amount
            elif option == "--":
                remaining.extend(args[index + 1 :])
                break
            elif option in ("-i", "-w", "-n", "-c", "-l", "-r"):
                ignore_case |= "i" in option[1:]
                whole_word |= "w" in option[1:]
                line_numbers |= "n" in option[1:]
                count_only |= "c" in option[1:]
                list_files |= "l" in option[1:]
                recursive |= "r" in option[1:]
            elif option.startswith("-") and option != "-":
                raise ValueError(f"Unsupported grep option: {option}")
            else:
                remaining.append(option)
            index += 1
        if not remaining:
            raise ValueError("Usage: grep [OPTIONS] PATTERN [FILE ...]")
        pattern = remaining[0]
        file_args = remaining[1:]
        files: list[tuple[str, str]] = []
        if file_args:
            paths = self.expand_paths(file_args)
            expanded_paths: list[Path] = []
            for path in paths:
                if path.is_dir():
                    if not recursive:
                        raise IsADirectoryError(f"Use grep -r to search a directory: {path.name}")
                    expanded_paths.extend(sorted(item.resolve() for item in path.rglob("*") if item.is_file()))
                else:
                    expanded_paths.append(path)
            for path in expanded_paths:
                files.append((path.relative_to(self.root).as_posix(), self.read_case_file(path)))
        elif stdin is not None:
            files.append(("", stdin))
        else:
            raise ValueError("Provide a file name or pipe text into grep.")

        flags = re.IGNORECASE if ignore_case else 0
        if whole_word:
            pattern = rf"\b(?:{pattern})\b"
        try:
            matcher = re.compile(pattern, flags)
        except re.error as exc:
            raise ValueError(f"Invalid search pattern: {exc}") from exc

        output: list[str] = []
        show_filename = len(files) > 1 or recursive
        for filename, text in files:
            lines = text.splitlines()
            matching = [idx for idx, line in enumerate(lines) if matcher.search(line)]
            if count_only:
                prefix = f"{filename}:" if show_filename else ""
                output.append(f"{prefix}{len(matching)}")
                continue
            if list_files:
                if matching:
                    output.append(filename or "(input)")
                continue
            selected: set[int] = set()
            for match_index in matching:
                selected.update(range(max(0, match_index - before), min(len(lines), match_index + after + 1)))
            previous = -2
            for line_index in sorted(selected):
                if (before or after) and previous >= 0 and line_index > previous + 1:
                    output.append("--")
                line = lines[line_index]
                is_match = line_index in matching
                if is_match and self.color_grep_matches:
                    line = matcher.sub(lambda match: self.colorize(match.group(0), "1;31"), line)
                prefix = f"{filename}:" if show_filename else ""
                if line_numbers:
                    prefix += f"{line_index + 1}:"
                output.append(f"{prefix}{line}")
                previous = line_index
        return "\n".join(output)

    def command_awk(self, args: list[str], stdin: str | None) -> str:
        field_separator: str | None = None
        remaining: list[str] = []
        index = 0
        while index < len(args) and args[index].startswith("-"):
            option = args[index]
            if option == "-F":
                index += 1
                if index >= len(args):
                    raise ValueError("-F needs a field separator.")
                field_separator = args[index]
            elif option.startswith("-F"):
                field_separator = option[2:]
            else:
                raise ValueError(f"Unsupported awk option: {option}")
            if not field_separator:
                raise ValueError("The awk field separator cannot be empty.")
            if field_separator == r"\t":
                field_separator = "\t"
            index += 1
        remaining = args[index:]
        if not remaining:
            raise ValueError("Usage: awk [-F SEPARATOR] PROGRAM [FILE ...]")

        program = re.fullmatch(
            r"\s*(?:/(?P<pattern>(?:\\.|[^/])*)/\s*)?"
            r"\{\s*(?P<body>.*?)\s*\}\s*",
            remaining[0],
        )
        if program is None:
            raise ValueError(
                "Supported awk syntax: [/PATTERN/] {print [$0|$N|$NF, ...]} "
                "or {if ($N == \"VALUE\") print ...}"
            )
        try:
            matcher = (
                re.compile(program["pattern"].replace(r"\/", "/"))
                if program["pattern"] is not None
                else None
            )
        except re.error as exc:
            raise ValueError(f"Invalid awk pattern: {exc}") from exc

        body = program["body"]
        condition_field = None
        condition_value = None
        if body.startswith("if"):
            condition = re.fullmatch(
                r"""if\s*\(\s*(?P<field>\$(?:0|[1-9]\d*|NF))\s*==\s*"""
                r"""(?P<quote>["'])(?P<value>.*?)(?P=quote)\s*\)\s*"""
                r"""(?P<action>print(?:\s+.*?)?)""",
                body,
            )
            if condition is None:
                raise ValueError(
                    'Supported awk conditions use: if ($N == "VALUE") print ...'
                )
            condition_field = condition["field"]
            condition_value = condition["value"]
            body = condition["action"]

        print_action = re.fullmatch(r"print(?:\s+(?P<fields>.*?))?", body)
        if print_action is None:
            raise ValueError("awk programs must use print, optionally inside a supported if.")
        expressions = (
            [field.strip() for field in print_action["fields"].split(",")]
            if print_action["fields"]
            else ["$0"]
        )
        if any(not re.fullmatch(r"\$(?:0|[1-9]\d*|NF)", field) for field in expressions):
            raise ValueError("awk print fields must be $0, a numbered field, or $NF.")

        file_args = remaining[1:]
        if file_args:
            text = self.read_paths(file_args)
        elif stdin is not None:
            text = stdin
        else:
            raise ValueError("Provide a file name or pipe text into awk.")

        def field_value(expression: str, line: str, fields: list[str]) -> str:
            if expression == "$0":
                return line
            if expression == "$NF":
                return fields[-1] if fields else ""
            field_index = int(expression[1:]) - 1
            return fields[field_index] if field_index < len(fields) else ""

        output = []
        for line in text.splitlines():
            if matcher is not None and matcher.search(line) is None:
                continue
            fields = line.split(field_separator) if field_separator else line.split()
            if (
                condition_field is not None
                and field_value(condition_field, line, fields) != condition_value
            ):
                continue
            values = [field_value(expression, line, fields) for expression in expressions]
            output.append(" ".join(values))
        return "\n".join(output)

    def command_lines(self, command: str, args: list[str], stdin: str | None) -> str:
        count = 10
        file_args = args[:]
        if file_args and file_args[0] == "-n":
            if len(file_args) < 2:
                raise ValueError(f"Usage: {command} -n N [FILE]")
            try:
                count = int(file_args[1].lstrip("+"))
                tail_from = command == "tail" and file_args[1].startswith("+")
            except ValueError as exc:
                raise ValueError("The line count must be an integer.") from exc
            file_args = file_args[2:]
        else:
            tail_from = False
        if file_args:
            text = self.read_paths(file_args)
        elif stdin is not None:
            text = stdin
        else:
            raise ValueError(f"Provide a file name or pipe text into {command}.")
        lines = text.splitlines()
        if command == "head" or count < 0:
            result = lines[:count] if count else []
        elif tail_from:
            result = lines[max(count - 1, 0) :]
        else:
            result = lines[-count:] if count else []
        return "\n".join(result)

    def command_wc(self, args: list[str], stdin: str | None) -> str:
        line_only = not args or "-l" in args
        file_args = [arg for arg in args if arg != "-l"]
        if file_args:
            paths = self.expand_paths(file_args)
            values = [(path.name, self.read_case_file(path)) for path in paths]
        elif stdin is not None:
            values = [("", stdin)]
        else:
            raise ValueError("Usage: wc [-l] FILE")
        results = []
        for name, text in values:
            if line_only:
                value = str(len(text.splitlines()))
            else:
                value = f"{len(text.splitlines())} {len(text.split())} {len(text.encode('utf-8'))}"
            results.append(f"{value} {name}".rstrip())
        return "\n".join(results)

    def execute_line(self, line: str) -> str:
        lexer = shlex.shlex(line, posix=True, punctuation_chars="|")
        lexer.whitespace_split = True
        tokens = list(lexer)
        if not tokens:
            return ""
        commands: list[list[str]] = [[]]
        for token in tokens:
            if token == "|":
                if not commands[-1]:
                    raise ValueError("A pipe must have a command on both sides.")
                commands.append([])
            else:
                commands[-1].append(token)
        if not commands[-1]:
            raise ValueError("A pipe must have a command on both sides.")
        output: str | None = None
        for index, command in enumerate(commands):
            if len(commands) > 1 and command[0] in ("cd", "hint", "check", "solution", "quit", "exit"):
                raise ValueError(f"`{command[0]}` cannot be used in a pipe.")
            self.color_grep_matches = self.color_enabled and index == len(commands) - 1
            output = self.execute_command(command, output)
        self.color_grep_matches = False
        result = output or ""
        check_command = len(commands) == 1 and commands[0][0] == "check"
        correct_answer = check_command and "CORRECT" in result
        if not (check_command and not correct_answer):
            self.successful_commands.append(line.strip())
        if correct_answer:
            return f"{result}\n\n{self.session_summary()}"
        return result

    def run(self) -> None:
        instructions = (ROOT / "instructions").read_text(encoding="utf-8")
        art, separator, body = instructions.partition(
            "\n\nThere's been a crime in Terminal City, and the police need your help.\n\n"
        )
        if not separator:
            raise ValueError("Instructions are missing the Terminal City introduction.")
        print(art.rstrip())
        print(self.colorize("THE COMMAND LINE MURDERS", "1;36"))
        print()
        intro = "There's been a crime in Terminal City, and the police need your help.\n\n" + body
        print(self.render_instructions(intro).rstrip())
        print()
        print(self.colorize(secrets.choice(WELCOME_MESSAGES), "1;32"))
        print("Type "
              f"{self.colorize('help', '1;36')} for commands, "
              f"{self.colorize('hint', '1;33')} for a clue, "
              f"{self.colorize('cheatsheet', '1;36')} for a reference, or "
              f"{self.colorize('check NAME', '1;32')} to test your answer.")
        if not self.enable_tab_completion():
            print("Tab completion is unavailable in this Python installation.")
        while self.running:
            try:
                prompt = f"{self.colorize(self.virtual_pwd(), '1;36')}$ "
                line = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                break
            try:
                output = self.execute_line(line)
            except (OSError, ValueError) as exc:
                print(f"Error: {exc}")
                continue
            if output:
                print(output)


def assign_case(*, new_case: bool = False) -> str:
    if not new_case and ASSIGNMENT_FILE.exists():
        assigned = ASSIGNMENT_FILE.read_text(encoding="utf-8").strip()
        if assigned not in CASES:
            raise ValueError(f"Invalid case assignment in {ASSIGNMENT_FILE}. Remove that file to assign a new case.")
        return assigned
    choices = list(CASES)
    if new_case and ASSIGNMENT_FILE.exists():
        previous = ASSIGNMENT_FILE.read_text(encoding="utf-8").strip()
        if previous in choices and len(choices) > 1:
            choices.remove(previous)
    assigned = secrets.choice(choices)
    ASSIGNMENT_FILE.write_text(f"{assigned}\n", encoding="utf-8")
    return assigned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Play a command-line mystery.")
    parser.add_argument(
        "--new-case",
        action="store_true",
        help="randomly assign a different case to this local copy",
    )
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="control terminal colors (default: auto)",
    )
    args = parser.parse_args(argv)
    try:
        case_key = assign_case(new_case=args.new_case)
        color_enabled = args.color == "always" or (
            args.color == "auto"
            and sys.stdout.isatty()
            and os.environ.get("TERM") != "dumb"
            and "NO_COLOR" not in os.environ
        )
        Game(CASES[case_key], color_enabled=color_enabled).run()
    except (OSError, ValueError) as exc:
        print(f"Unable to start the game: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
