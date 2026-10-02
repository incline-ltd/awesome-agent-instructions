"""Boundary and byte-accounting tests using only synthetic instruction text."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "skills/trim-instructions/scripts/measure.py"
SPEC = importlib.util.spec_from_file_location("measure", SCRIPT)
measure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(measure)


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def write(self, path, content=b"A rule.\n"):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def test_unicode_crlf_and_sha256_preserve_exact_bytes(self):
        raw = "Keep café 🐈.\r\n".encode("utf-8")
        self.write("AGENTS.md", raw)
        report = measure.measure_files(self.root, ["AGENTS.md"])
        item = report["files"][0]
        self.assertEqual(item["bytes"], len(raw))
        self.assertEqual(item["characters"], len(raw.decode("utf-8")))
        self.assertEqual(item["estimated_tokens"], (len(raw.decode("utf-8")) + 3) // 4)
        self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(report["scope"], "selected_files_only")

    def test_totals_sum_rounded_file_estimates(self):
        self.write("AGENTS.md", b"a")
        self.write("CLAUDE.md", b"b")
        report = measure.measure_files(self.root, ["CLAUDE.md", "AGENTS.md"])
        self.assertEqual(report["totals"], {"files": 2, "bytes": 2, "characters": 2, "estimated_tokens": 2})
        self.assertEqual([item["path"] for item in report["files"]], ["AGENTS.md", "CLAUDE.md"])
        self.assertEqual(report, measure.measure_files(self.root, ["AGENTS.md", "CLAUDE.md"]))

    def test_duplicates_are_counted_once_without_discovery(self):
        self.write("AGENTS.md", b"abcd")
        self.write("nested/AGENTS.md", b"This file was not selected.")
        report = measure.measure_files(self.root, ["AGENTS.md", "./AGENTS.md", "AGENTS.md"])
        self.assertEqual(report["totals"]["files"], 1)
        self.assertEqual(report["totals"]["bytes"], 4)
        self.assertEqual(report["duplicates_skipped"], 2)

    def test_distinct_hardlink_paths_keep_roles_and_are_counted_separately(self):
        raw = b"---\nname: sample\n---\nBody.\n"
        source = self.write("AGENTS.md", raw)
        os.link(source, self.root / "SKILL.md")
        report = measure.measure_files(self.root, ["AGENTS.md", "SKILL.md", "./SKILL.md"])
        self.assertEqual(report["totals"]["files"], 2)
        self.assertEqual(report["totals"]["bytes"], 2 * len(raw))
        self.assertEqual(report["duplicates_skipped"], 1)
        self.assertEqual(report["deduplication"], "normalized_paths_only")
        agent_file, skill_file = report["files"]
        self.assertEqual(agent_file["sha256"], skill_file["sha256"])
        self.assertNotIn("frontmatter", agent_file)
        self.assertEqual(skill_file["frontmatter"]["status"], "delimited")

    def test_empty_file_has_zero_estimate(self):
        self.write("AGENTS.md", b"")
        self.assertEqual(measure.measure_files(self.root, ["AGENTS.md"])["totals"],
                         {"files": 1, "bytes": 0, "characters": 0, "estimated_tokens": 0})

    def test_known_instruction_formats_and_scoped_claude_rules(self):
        paths = sorted(measure.INSTRUCTION_NAMES) + ["rules/testing.mdc", ".github/path.instructions.md",
                                                   ".claude/rules/nested/testing.md"]
        for path in paths:
            self.write(path)
        self.assertEqual(measure.measure_files(self.root, paths)["totals"]["files"], len(paths))
        nested_root = self.root / ".claude/rules"
        self.assertEqual(measure.measure_files(nested_root, ["nested/testing.md"])["totals"]["files"], 1)

    def test_arbitrary_markdown_requires_reference_flag(self):
        self.write("references/testing.md")
        with self.assertRaises(measure.MeasurementError):
            measure.measure_files(self.root, ["references/testing.md"])
        self.assertEqual(measure.measure_files(self.root, ["references/testing.md"], allow_reference=True)["totals"]["files"], 1)
        self.write("references/testing.txt")
        with self.assertRaises(measure.MeasurementError):
            measure.measure_files(self.root, ["references/testing.txt"], allow_reference=True)

    def test_absolute_traversal_windows_and_control_paths_are_rejected(self):
        self.write("AGENTS.md")
        for path in [str(self.root / "AGENTS.md"), "../AGENTS.md", "nested/../AGENTS.md", "C:/AGENTS.md",
                     "C:AGENTS.md", "nested\\AGENTS.md", "\nAGENTS.md", "", "."]:
            with self.subTest(path=repr(path)), self.assertRaises(measure.MeasurementError):
                measure.measure_files(self.root, [path], allow_reference=True)

    def test_secret_like_inputs_are_excluded_even_with_reference_flag(self):
        for path in [".env", ".env.production", ".env.md", ".envrc", ".ssh/AGENTS.md", ".aws/AGENTS.md",
                     ".git/AGENTS.md", "credentials.md", "secrets.md", "private-key.md", "api_key.md",
                     "id_rsa.md", "nested/config.env", "nested/server.pem"]:
            self.write(path)
            with self.subTest(path=path), self.assertRaises(measure.MeasurementError):
                measure.measure_files(self.root, [path], allow_reference=True)
        with self.assertRaises(measure.MeasurementError):
            measure.measure_files(self.root / ".ssh", ["AGENTS.md"])

    def test_secret_like_root_components_cannot_bypass_path_exclusion(self):
        for folder in ["secrets", "credentials", ".env", ".env.private", "private-key", "nested/secrets/deeper"]:
            self.write(f"{folder}/AGENTS.md")
            output, errors = io.StringIO(), io.StringIO()
            with self.subTest(folder=folder), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                self.assertEqual(measure.main(["--root", str(self.root / folder), "AGENTS.md"]), 2)
            self.assertEqual(output.getvalue(), "")
            self.assertNotIn(str(self.root), errors.getvalue())
            self.assertNotIn(folder, errors.getvalue())

    def test_leaf_and_parent_symlinks_are_rejected_even_inside_root(self):
        self.write("real/AGENTS.md")
        (self.root / "CLAUDE.md").symlink_to("real/AGENTS.md")
        (self.root / "alias").symlink_to("real", target_is_directory=True)
        for path in ["CLAUDE.md", "alias/AGENTS.md"]:
            with self.subTest(path=path), self.assertRaises(measure.MeasurementError):
                measure.measure_files(self.root, [path])

    def test_symlink_escape_and_symlink_root_are_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            other = Path(outside).resolve()
            (other / "AGENTS.md").write_bytes(b"External content.")
            (self.root / "escape").symlink_to(other, target_is_directory=True)
            with self.assertRaises(measure.MeasurementError):
                measure.measure_files(self.root, ["escape/AGENTS.md"])
            with self.assertRaises(measure.MeasurementError):
                measure.measure_files(self.root / "escape", ["AGENTS.md"])

    def test_portable_fallback_rejects_static_symlinks(self):
        self.write("real/AGENTS.md")
        (self.root / "alias").symlink_to("real", target_is_directory=True)
        with mock.patch.object(measure.os, "supports_dir_fd", set()):
            self.assertEqual(measure.measure_files(self.root, ["real/AGENTS.md"])["totals"]["files"], 1)
            with self.assertRaises(measure.MeasurementError):
                measure.measure_files(self.root, ["alias/AGENTS.md"])

    def test_directories_missing_files_and_non_utf8_are_rejected(self):
        (self.root / "AGENTS.md").mkdir()
        self.write("CLAUDE.md", b"\xff\xfe")
        for path in ["AGENTS.md", "GEMINI.md", "CLAUDE.md"]:
            with self.subTest(path=path), self.assertRaises(measure.MeasurementError):
                measure.measure_files(self.root, [path])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "Named pipes are unavailable on this platform")
    def test_fifo_is_rejected_without_opening_it(self):
        os.mkfifo(self.root / "AGENTS.md")
        with self.assertRaises(measure.MeasurementError):
            measure.measure_files(self.root, ["AGENTS.md"])

    def test_file_count_individual_size_and_total_size_are_bounded(self):
        self.write("AGENTS.md", b"a" * (measure.MAX_FILE_BYTES + 1))
        with self.assertRaises(measure.MeasurementError):
            measure.measure_files(self.root, ["AGENTS.md"])
        with self.assertRaises(measure.MeasurementError):
            measure.measure_files(self.root, ["AGENTS.md"] * (measure.MAX_FILES + 1))
        with self.assertRaises(measure.MeasurementError):
            measure.measure_files(self.root, [])
        self.write("AGENTS.md", b"a" * 5)
        self.write("CLAUDE.md", b"b" * 5)
        with mock.patch.object(measure, "MAX_TOTAL_BYTES", 9), self.assertRaises(measure.MeasurementError):
            measure.measure_files(self.root, ["AGENTS.md", "CLAUDE.md"])

    def test_frontmatter_counts_include_delimiters_without_normalizing_newlines(self):
        metadata = "---\r\nname: example\r\n---\r\n"
        body = "# Keep this\r\n"
        self.write("SKILL.md", (metadata + body).encode("utf-8"))
        sections = measure.measure_files(self.root, ["SKILL.md"])["files"][0]["frontmatter"]
        self.assertEqual(sections["status"], "delimited")
        self.assertEqual(sections["metadata"]["characters"], len(metadata))
        self.assertEqual(sections["body"]["characters"], len(body))

    def test_frontmatter_accepts_bom_and_yaml_end_delimiter(self):
        metadata = "\ufeff---\nname: sample\n...\n"
        self.write("SKILL.md", (metadata + "Body.").encode("utf-8"))
        sections = measure.measure_files(self.root, ["SKILL.md"])["files"][0]["frontmatter"]
        self.assertEqual(sections["status"], "delimited")
        self.assertEqual(sections["metadata"]["bytes"], len(metadata.encode("utf-8")))
        self.assertEqual(sections["body"]["characters"], 5)

    def test_malformed_frontmatter_reports_diagnostic_but_keeps_total(self):
        raw = b"---\nname: sample\nNo closing delimiter.\n"
        self.write("SKILL.md", raw)
        item = measure.measure_files(self.root, ["SKILL.md"])["files"][0]
        self.assertEqual(item["bytes"], len(raw))
        self.assertEqual(item["frontmatter"]["status"], "malformed")
        self.assertNotIn("body", item["frontmatter"])

    def test_delimited_frontmatter_does_not_claim_yaml_validation(self):
        self.write("SKILL.md", b"---\n: [invalid\n---\nBody")
        report = measure.measure_files(self.root, ["SKILL.md"])
        self.assertEqual(report["files"][0]["frontmatter"]["status"], "delimited")
        self.assertIn("do not validate YAML", report["caveat"])

    def test_no_frontmatter_treats_whole_skill_as_body(self):
        self.write("SKILL.md", b"# Skill\n---\nBody")
        item = measure.measure_files(self.root, ["SKILL.md"])["files"][0]
        self.assertEqual(item["frontmatter"]["status"], "absent")
        self.assertEqual(item["frontmatter"]["body"]["bytes"], item["bytes"])
        self.assertEqual(item["frontmatter"]["metadata"]["estimated_tokens"], 0)

    def test_cli_json_is_deterministic_and_contains_no_content_or_absolute_paths(self):
        marker = b"UNIQUE_PRIVATE_CONTENT_MARKER"
        self.write("AGENTS.md", marker)
        outputs = []
        for _ in range(2):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(measure.main(["--root", str(self.root), "AGENTS.md", "--json"]), 0)
            outputs.append(output.getvalue())
        self.assertEqual(outputs[0], outputs[1])
        self.assertNotIn(str(self.root), outputs[0])
        self.assertNotIn(marker.decode(), outputs[0])
        self.assertEqual(json.loads(outputs[0])["files"][0]["path"], "AGENTS.md")
        self.assertEqual((self.root / "AGENTS.md").read_bytes(), marker)
        self.assertEqual(list(self.root.iterdir()), [self.root / "AGENTS.md"])

    def test_cli_human_output_is_content_free_and_error_returns_no_partial_report(self):
        marker = b"NEVER_PRINT_THIS_CONTENT"
        self.write("AGENTS.md", marker)
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(measure.main(["--root", str(self.root), "AGENTS.md"]), 0)
        self.assertNotIn(marker.decode(), output.getvalue())
        self.assertIn("not live session token usage", output.getvalue())
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(measure.main(["--root", str(self.root), "AGENTS.md", "GEMINI.md", "--json"]), 2)
        self.assertEqual(output.getvalue(), "")
        self.assertNotIn(marker.decode(), errors.getvalue())
        self.assertNotIn(str(self.root), errors.getvalue())

    def test_argument_errors_do_not_echo_unrecognized_values_or_paths(self):
        marker = "SYNTHETIC_PRIVATE_VALUE"
        cases = [
            ["--root", str(self.root), "AGENTS.md", f"--unknown={marker}"],
            ["--root", str(self.root), "AGENTS.md", "--unknown", marker],
            ["--root"],
        ]
        for arguments in cases:
            output, errors = io.StringIO(), io.StringIO()
            with self.subTest(arguments=arguments), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                self.assertEqual(measure.main(arguments), 2)
            self.assertEqual(output.getvalue(), "")
            self.assertEqual(errors.getvalue(), "Error: Invalid arguments; run measure.py --help for usage.\n")
            self.assertNotIn(marker, errors.getvalue())
            self.assertNotIn(str(self.root), errors.getvalue())


if __name__ == "__main__":
    unittest.main()
