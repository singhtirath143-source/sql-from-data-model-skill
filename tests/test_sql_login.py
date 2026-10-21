import contextlib
import importlib.util
import io
import json
import os
import re
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".cursor/skills/sql-from-data-model-skill/scripts/sql_login.py"
QUERIES = ROOT / ".cursor/skills/sql-from-data-model-skill/catalog/queries.md"
EXAMPLE = ROOT / ".cursor/skills/sql-from-data-model-skill/scripts/databases.example.json"

spec = importlib.util.spec_from_file_location("sql_login", SCRIPT)
sql_login = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sql_login)


def catalog_scripts():
    text = QUERIES.read_text(encoding="utf-8")
    return re.findall(r"```sql\n(.*?)```", text, re.S)


def catalog_step(number):
    text = QUERIES.read_text(encoding="utf-8")
    match = re.search(rf"^## Step {number}\b.*?```sql\n(.*?)```", text, re.S | re.M)
    return match.group(1)


class CatalogQueriesTextTests(unittest.TestCase):
    def test_step3_never_drops_a_column(self):
        step3 = catalog_step(3)
        self.assertNotRegex(step3, r"(?i)INNER\s+JOIN\s+sys\.types")
        self.assertIn("LEFT JOIN sys.types AS ty ON ty.user_type_id = c.user_type_id", step3)
        self.assertIn("LEFT JOIN sys.types AS bt ON bt.user_type_id = c.system_type_id", step3)

    def test_step3_type_display_uses_the_base_type(self):
        step3 = catalog_step(3)
        self.assertNotIn("THEN ty.name", step3)
        self.assertIn("COALESCE(ty.name, bt.name, N'unknown') AS type_name", step3)

    def test_step3_returns_has_default(self):
        self.assertIn(
            "CASE WHEN dc.object_id IS NULL THEN 0 ELSE 1 END AS has_default",
            catalog_step(3),
        )

    def test_step2_returns_column_count(self):
        self.assertIn(
            "(SELECT COUNT(*) FROM sys.columns AS c WHERE c.object_id = t.object_id) AS column_count",
            catalog_step(2),
        )

    def test_step1_returns_can_view_definitions(self):
        self.assertIn(
            "HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'VIEW DEFINITION') AS can_view_definitions",
            catalog_step(1),
        )


OLD_EMPTY_DEFINITION_WORDING = (
    "definition null",
    "cannot tell a hidden default from no default",
)


def doc_files():
    return [ROOT / "AGENTS.md", ROOT / "README.md", *sorted((ROOT / ".cursor/skills").rglob("*.md"))]


class DocsWordingTests(unittest.TestCase):
    def test_no_doc_has_the_old_empty_definition_wording(self):
        files = doc_files()
        self.assertGreater(len(files), 3)
        for path in files:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in OLD_EMPTY_DEFINITION_WORDING:
                self.assertNotIn(phrase, text, f"{path.relative_to(ROOT)}: {phrase}")

    def test_docs_share_the_hidden_definitions_line(self):
        line = (
            "This login cannot view definitions, so check-constraint rules, column defaults "
            "and some procedures and functions are not shown."
        )
        skill = ROOT / ".cursor/skills/sql-from-data-model-skill"
        for path in (skill / "catalog/build.md", skill / "SKILL.md", ROOT / "AGENTS.md", ROOT / "README.md"):
            self.assertIn(line, path.read_text(encoding="utf-8"), path.relative_to(ROOT))


class SkillNameTests(unittest.TestCase):
    NAME = "sql-from-data-model-skill"

    def test_folder_and_frontmatter_name_match(self):
        skill = ROOT / ".cursor/skills" / self.NAME / "SKILL.md"
        self.assertRegex(skill.read_text(encoding="utf-8"), rf"(?m)^name: {self.NAME}$")

    def test_no_doc_uses_the_old_command_or_folder(self):
        for path in doc_files():
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?<![\w/.\\])/sql-from-data-model(?![\w-])", path.relative_to(ROOT))
            self.assertNotRegex(text, r"\.cursor/skills/sql-from-data-model(?![\w-])", path.relative_to(ROOT))


class GuardTests(unittest.TestCase):
    def test_catalog_scripts_pass(self):
        blocks = catalog_scripts()
        self.assertEqual(len(blocks), 7)
        for index, block in enumerate(blocks, start=1):
            self.assertIsNone(sql_login.refuse_reason(block), f"catalog step {index}")

    def test_string_comment_and_system_variable_pass(self):
        self.assertIsNone(sql_login.refuse_reason("SELECT 'declare' AS word;"))
        self.assertIsNone(sql_login.refuse_reason("-- declare a variable\nSELECT 1;"))
        self.assertIsNone(sql_login.refuse_reason("SELECT @@SERVERNAME;"))

    def test_leading_semicolon_with_passes(self):
        sql = ";WITH x AS (SELECT 1 AS a) SELECT * FROM x;"
        self.assertIsNone(sql_login.refuse_reason(sql))

    def test_catalog_set_lines_pass(self):
        self.assertIsNone(sql_login.refuse_reason("SET NOCOUNT ON; SELECT 1;"))

    def test_semicolon_inside_a_string_passes(self):
        self.assertIsNone(sql_login.refuse_reason("SELECT 'a;b' AS t;"))

    def test_bracketed_name_and_literal_pass(self):
        sql = "SELECT o.OrderNumber FROM dbo.[Order] AS o WHERE o.CustomerId = N'C-1001';"
        self.assertIsNone(sql_login.refuse_reason(sql))

    def test_multiline_join_passes(self):
        sql = """
SELECT c.CustomerId, o.OrderNumber
FROM dbo.Customer AS c
JOIN dbo.[Order] AS o ON o.CustomerId = c.CustomerId
WHERE c.CustomerId = N'C-1001'
"""
        self.assertIsNone(sql_login.refuse_reason(sql))

    def test_declare_uses_the_declare_message(self):
        reason = sql_login.refuse_reason("DECLARE @x INT = 1;\nSELECT @x;")
        self.assertEqual(reason, sql_login.DECLARE_MESSAGE)

    def test_procedure_name_without_exec_stops(self):
        reason = sql_login.refuse_reason("sp_who")
        self.assertEqual(
            reason,
            'statement 1 starts with "sp_who". Only SELECT and WITH queries are allowed.',
        )

    def test_use_stops(self):
        reason = sql_login.refuse_reason("USE master; SELECT 1;")
        self.assertIn('statement 1 starts with "USE master"', reason)

    def test_blank_line_starts_a_new_statement(self):
        reason = sql_login.refuse_reason("SELECT 1\n\nsp_who")
        self.assertIn('statement 2 starts with "sp_who"', reason)

    def test_comment_markers_inside_strings_do_not_hide_sql(self):
        self.assertIsNotNone(sql_login.refuse_reason("SELECT 'x--'; DELETE FROM dbo.T;"))
        self.assertIsNotNone(sql_login.refuse_reason("SELECT 'x--';\nsp_who"))
        hidden = "SELECT '/*' AS a; DROP TABLE dbo.T; SELECT '*/' AS b;"
        self.assertIsNotNone(sql_login.refuse_reason(hidden))

    def test_semicolon_does_not_merge_a_continuation(self):
        self.assertIsNotNone(sql_login.refuse_reason("SELECT 1;\nLEFT sp_who"))

    def test_real_comment_between_selects_passes(self):
        sql = "SELECT 'a' AS x;\n-- note\nSELECT 'b--c' AS y;"
        self.assertIsNone(sql_login.refuse_reason(sql))

    def test_nested_block_comment_passes(self):
        sql = "SELECT 1 /* outer /* inner */ still comment */ AS a;"
        self.assertIsNone(sql_login.refuse_reason(sql))

    def test_unclosed_string_stops(self):
        self.assertEqual(sql_login.refuse_reason("SELECT 'unclosed"), sql_login.UNCLOSED_MESSAGE)

    def test_write_statements_stop(self):
        blocked = [
            "WITH x AS (SELECT 1 AS a) DELETE FROM dbo.T;",
            "SELECT * INTO #t FROM dbo.X;",
            "INSERT INTO dbo.X VALUES (1);",
            "SET ANSI_NULLS OFF; SELECT 1;",
            "SELECT * FROM OPENROWSET('SQLNCLI', 'x', 'SELECT 1');",
            "EXEC sp_who;",
        ]
        for sql in blocked:
            self.assertIsNotNone(sql_login.refuse_reason(sql), sql)

    def test_lone_name_stops(self):
        cases = {
            "[usp_Purge]": 1,
            '"usp_Purge"': 1,
            "SELECT 1;\n[usp_Purge]": 2,
            'SELECT 1;\n"usp_Purge"': 2,
            "[dbo].[usp_Purge]": 1,
        }
        for sql, index in cases.items():
            reason = sql_login.refuse_reason(sql)
            self.assertIsNotNone(reason, sql)
            self.assertIn(f"statement {index} starts with", reason, sql)

    def test_bracketed_names_in_a_select_pass(self):
        sql = "SELECT [a] FROM [dbo].[T] WHERE [b] = N'O''Brien';"
        self.assertIsNone(sql_login.refuse_reason(sql))
        self.assertIsNone(sql_login.refuse_reason('SELECT "a" FROM "dbo"."T";'))

    def test_next_value_for_stops(self):
        for sql in (
            "SELECT NEXT VALUE FOR dbo.Seq;",
            "select next value for [dbo].[Seq];",
            "SELECT NEXT\n  VALUE /* x */ FOR dbo.Seq;",
        ):
            self.assertEqual(
                sql_login.refuse_reason(sql),
                "the query contains NEXT VALUE FOR. Only SELECT and WITH are allowed.",
                sql,
            )

    def test_next_value_for_inside_a_string_passes(self):
        self.assertIsNone(sql_login.refuse_reason("SELECT 'NEXT VALUE FOR dbo.Seq' AS words;"))
        self.assertIsNone(sql_login.refuse_reason("SELECT 1 AS [NEXT VALUE FOR];"))

    def test_doubled_apostrophe_passes(self):
        self.assertIsNone(sql_login.refuse_reason("SELECT 1 WHERE Name = N'O''Brien';"))

    def test_single_apostrophe_stops_with_the_hint(self):
        reason = sql_login.refuse_reason("SELECT 1 WHERE Name = N'O'Brien';")
        self.assertEqual(reason, sql_login.UNCLOSED_MESSAGE)
        self.assertIn("write it twice, for example N'O''Brien'", reason)

    def test_declare_message_has_the_hint(self):
        self.assertIn("N'O''Brien'", sql_login.DECLARE_MESSAGE)


class RoleResultTests(unittest.TestCase):
    DB = "app_db"

    def table(self, reader, writer, owner):
        return (
            "|database_name|reader_role|writer_role|owner_role|\n"
            "|-------------|-----------|-----------|----------|\n"
            f"|{self.DB}|{reader}|{writer}|{owner}|\n"
        )

    def test_reader_only_is_read_only(self):
        self.assertEqual(sql_login.role_result(self.table(1, 0, 0), self.DB), "read-only")

    def test_reader_zero_is_read_only(self):
        self.assertEqual(sql_login.role_result(self.table(0, 0, 0), self.DB), "read-only")

    def test_writer_can_change_data(self):
        self.assertEqual(sql_login.role_result(self.table(1, 1, 0), self.DB), "can change data")

    def test_owner_can_change_data(self):
        self.assertEqual(sql_login.role_result(self.table(0, 0, 1), self.DB), "can change data")

    def test_missing_row(self):
        self.assertEqual(sql_login.role_result("", self.DB), "missing")
        self.assertEqual(sql_login.role_result(self.table(1, 0, 0), "other_db"), "missing")
        self.assertEqual(sql_login.role_result(f"|{self.DB}|1|\n", self.DB), "missing")


class QueriesPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.paths = sql_login.config_paths(self.root / "settings")

    def tearDown(self):
        self.tmp.cleanup()

    def test_next_to_a_named_model(self):
        setup = {"model_path": str(self.root / "models" / "app-data-model.md")}
        self.assertEqual(
            sql_login.queries_path(setup, self.paths),
            self.root / "models" / "app-data-model.saved-queries.md",
        )

    def test_next_to_the_default_model(self):
        self.assertEqual(
            sql_login.queries_path(sql_login.empty_setup(), self.paths),
            self.root / "settings" / "data-model.saved-queries.md",
        )

    def test_paths_prints_it(self):
        model = self.root / "models" / "my-model.md"
        sql_login.save_setup({"model_path": str(model)}, self.paths)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sql_login.print_paths(self.paths)
        lines = out.getvalue().splitlines()
        self.assertIn(f"model_path={model}", lines)
        self.assertIn(f"queries_path={model.with_name('my-model.saved-queries.md')}", lines)


class CountTableRowsTests(unittest.TestCase):
    def test_three_rows(self):
        output = """\
| id | name |
|----|------|
| 1  | a    |
| 2  | b    |
| 3  | c    |
"""
        self.assertEqual(sql_login.count_table_rows(output), 3)
        self.assertIsNone(sql_login.pipe_value_note(output))

    def test_comma_value_and_blank_cell(self):
        output = """\
| status | total |
|--------|-------|
| Open   | 8,292 |
| Closed |       |
"""
        self.assertEqual(sql_login.count_table_rows(output), 2)
        self.assertIsNone(sql_login.pipe_value_note(output))

    def test_header_and_separator_only(self):
        output = "| CustomerId |\n|------------|\n"
        self.assertEqual(sql_login.count_table_rows(output), 0)

    def test_no_pipe_lines(self):
        self.assertEqual(sql_login.count_table_rows("no table here\n"), 0)
        self.assertEqual(sql_login.count_table_rows(""), 0)
        self.assertEqual(sql_login.count_table_rows(None), 0)

    def test_dbvr_empty_result(self):
        # Empty dbvr result: a header and a separator, and no data row.
        output = """\
|CustomerId|
|----------|
"""
        self.assertEqual(sql_login.count_table_rows(output), 0)
        self.assertIsNone(sql_login.pipe_value_note(output))

    def test_extra_pipe_still_counts_and_notes(self):
        output = """\
| id | name |
|----|------|
| 1  | a|b  |
"""
        self.assertEqual(sql_login.count_table_rows(output), 1)
        self.assertEqual(sql_login.pipe_value_note(output), sql_login.PIPE_VALUE_NOTE)
        self.assertEqual(
            sql_login.PIPE_VALUE_NOTE,
            'NOTE a value contains "|", so this table may display wrong',
        )


class OtherChecks(unittest.TestCase):
    def test_version_ok(self):
        self.assertTrue(sql_login.version_ok("dbvr 26.2.2.202610041844"))
        self.assertFalse(sql_login.version_ok("26.1.9"))
        self.assertTrue(sql_login.version_ok("27.0"))

    def test_settings_dir(self):
        windows = sql_login.settings_dir(
            "win32",
            {"APPDATA": "C:/AppData/Roaming"},
            "C:/home/a",
        )
        self.assertEqual(windows, Path("C:/AppData/Roaming") / "sql-from-data-model")
        home = Path("/tmp/sql-login-home")
        mac = sql_login.settings_dir("darwin", {}, home)
        self.assertEqual(mac, home / ".config" / "sql-from-data-model")

    def test_validate_databases(self):
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(sql_login.validate_databases(data), [])
        data["environments"][0]["databases"][0]["password"] = "nope"
        errors = sql_login.validate_databases(data)
        self.assertTrue(any("password" in error for error in errors))

    def test_old_env_credentials_are_complete(self):
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        rows = sql_login.flatten_databases(data)
        values = {"SQL_USER": "shared-user"}
        for row in rows:
            values[sql_login.password_env_key(row["key"])] = "saved-password"
        self.assertEqual(sql_login.credentials_complete(values, rows), [])
        self.assertEqual(len(rows), 4)

    def test_redact_and_error_mapping(self):
        redact = sql_login.make_redact(["saved-password"])
        self.assertEqual(redact("pw saved-password"), "pw [hidden]")
        firewall = sql_login.map_dbvr_error(
            "Client with IP address 10.0.0.1 is not allowed to access the server",
            "App",
            "Dev",
        )
        self.assertIn("firewall is blocking your IP address", firewall)
        login = sql_login.map_dbvr_error(
            "Login failed for user 'reader'.",
            "App",
            "Dev",
        )
        self.assertEqual(login, "Wrong username or password for App Dev.")

    def test_decode_output(self):
        self.assertEqual(sql_login.decode_output("📣".encode("utf-8")), "📣")
        decoded = sql_login.decode_output(b"\xff\xfe")
        self.assertIsInstance(decoded, str)

    def test_builtin_database_list_option_is_gone(self):
        self.assertFalse(hasattr(sql_login, "OLD_SETUP"))
        scripts = ROOT / ".cursor/skills/sql-from-data-model-skill/scripts"
        names = sorted(path.name for path in scripts.glob("*.json"))
        self.assertEqual(names, ["databases.example.json"])
        with tempfile.TemporaryDirectory() as root:
            paths = sql_login.config_paths(Path(root) / "settings")
            previous = os.getcwd()
            os.chdir(root)
            try:
                with self.assertRaises(SystemExit) as raised:
                    with contextlib.redirect_stdout(io.StringIO()) as out:
                        sql_login.init_databases("builtin", paths)
                self.assertEqual(raised.exception.code, 1)
                self.assertIn("database file not found", out.getvalue())
                self.assertNotIn("OK databases", out.getvalue())
                self.assertFalse(paths["databases_json"].exists())
            finally:
                os.chdir(previous)

    def test_init_databases_copies_example_file(self):
        with tempfile.TemporaryDirectory() as root:
            paths = sql_login.config_paths(root)
            with contextlib.redirect_stdout(io.StringIO()):
                sql_login.init_databases(str(EXAMPLE), paths)
            saved = json.loads(paths["databases_json"].read_text(encoding="utf-8"))
            self.assertEqual(sql_login.validate_databases(saved), [])
            labels = [row["label"] for row in sql_login.flatten_databases(saved)]
            self.assertEqual(labels, ["App", "Reporting", "App", "Reporting"])

    def test_repo_links_accept_arbitrary_labels(self):
        with tempfile.TemporaryDirectory() as root:
            paths = sql_login.config_paths(root)
            sql_login.save_setup(
                {
                    "source": "repos",
                    "repo_links": {
                        "App": "https://example.com/app.git",
                        "Reporting": "https://example.com/reporting.git",
                        "Billing": "https://example.com/billing.git",
                        "  ": "https://example.com/blank.git",
                    },
                    "read_access_confirmed": True,
                    "password": "do-not-keep",
                },
                paths,
            )
            saved = json.loads(paths["setup_json"].read_text(encoding="utf-8"))
            self.assertEqual(
                saved["repo_links"],
                {
                    "App": "https://example.com/app.git",
                    "Reporting": "https://example.com/reporting.git",
                    "Billing": "https://example.com/billing.git",
                },
            )
            self.assertNotIn("password", saved)
            self.assertEqual(saved["source"], "repos")
            self.assertTrue(saved["read_access_confirmed"])
            self.assertEqual(saved["notes_path"], "")
            if os.name != "nt":
                mode = paths["setup_json"].stat().st_mode & 0o777
                self.assertEqual(mode, 0o600)

    def test_notes_path_is_optional(self):
        empty = sql_login.empty_setup()
        self.assertEqual(empty["notes_path"], "")
        self.assertEqual(sql_login.clean_setup({"source": "dbvr"})["notes_path"], "")
        kept = sql_login.clean_setup(
            {
                "source": "dbvr",
                "notes_path": "/tmp/column-notes.md",
                "read_access_confirmed": False,
            }
        )
        self.assertEqual(kept["notes_path"], "/tmp/column-notes.md")
        finished = sql_login.clean_setup(
            {
                "source": "dbvr",
                "dbvr_path": "/opt/dbvr",
                "model_path": "/tmp/data-model.md",
            }
        )
        self.assertEqual(finished["source"], "dbvr")
        self.assertEqual(finished["model_path"], "/tmp/data-model.md")
        self.assertEqual(finished["notes_path"], "")
        self.assertEqual(finished["repo_links"], {})


class DbvrEnvTests(unittest.TestCase):
    OPTION = "-Dstdout.encoding=UTF-8"

    def test_windows_adds_the_option(self):
        env = sql_login.dbvr_env("win32", {"PATH": "C:/bin"})
        self.assertEqual(env["JAVA_TOOL_OPTIONS"], self.OPTION)
        self.assertEqual(env["PATH"], "C:/bin")

    def test_windows_keeps_an_existing_value(self):
        env = sql_login.dbvr_env("win32", {"JAVA_TOOL_OPTIONS": "-Xmx512m"})
        self.assertEqual(env["JAVA_TOOL_OPTIONS"], f"-Xmx512m {self.OPTION}")

    def test_windows_does_not_add_it_twice(self):
        for value in (self.OPTION, f"-Xmx512m {self.OPTION}"):
            env = sql_login.dbvr_env("win32", {"JAVA_TOOL_OPTIONS": value})
            self.assertEqual(env["JAVA_TOOL_OPTIONS"], value)
            env = sql_login.dbvr_env("win32", env)
            self.assertEqual(env["JAVA_TOOL_OPTIONS"].split().count(self.OPTION), 1)

    def test_mac_and_linux_are_unchanged(self):
        for platform in ("darwin", "linux"):
            source = {"PATH": "/usr/bin", "JAVA_TOOL_OPTIONS": "-Xmx512m"}
            self.assertEqual(sql_login.dbvr_env(platform, source), source)
            self.assertNotIn("JAVA_TOOL_OPTIONS", sql_login.dbvr_env(platform, {"PATH": "/usr/bin"}))

    def test_caller_environment_is_not_modified(self):
        source = {"JAVA_TOOL_OPTIONS": "-Xmx512m"}
        env = sql_login.dbvr_env("win32", source)
        self.assertEqual(source, {"JAVA_TOOL_OPTIONS": "-Xmx512m"})
        self.assertIsNot(env, source)
        empty = {}
        sql_login.dbvr_env("win32", empty)
        self.assertEqual(empty, {})

    def test_run_dbvr_passes_the_environment(self):
        seen = {}

        def fake_run(cmd, **kwargs):
            seen.update(kwargs)
            return subprocess.CompletedProcess(cmd, 0, stdout=b"|a|\n|-|\n|1|\n", stderr=b"")

        with mock.patch.object(sql_login.subprocess, "run", fake_run):
            proc = sql_login.run_dbvr(["dbvr"], timeout=5)
        self.assertEqual(seen["env"], sql_login.dbvr_env())
        self.assertEqual(seen["timeout"], 5)
        self.assertEqual(proc.stdout, "|a|\n|-|\n|1|\n")


if __name__ == "__main__":
    unittest.main()
