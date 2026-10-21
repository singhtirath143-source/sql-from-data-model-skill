import contextlib
import importlib.util
import io
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".cursor/skills/sql-from-data-model/scripts/sql_login.py"
QUERIES = ROOT / ".cursor/skills/sql-from-data-model/catalog/queries.md"
EXAMPLE = ROOT / ".cursor/skills/sql-from-data-model/scripts/databases.example.json"

spec = importlib.util.spec_from_file_location("sql_login", SCRIPT)
sql_login = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sql_login)


def catalog_scripts():
    text = QUERIES.read_text(encoding="utf-8")
    return re.findall(r"```sql\n(.*?)```", text, re.S)


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
        scripts = ROOT / ".cursor/skills/sql-from-data-model/scripts"
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


class AnyLoginTests(unittest.TestCase):
    def table(self, reader, writer, owner):
        return (
            "|database_name|reader_role|writer_role|owner_role|\n"
            "|-------------|-----------|-----------|----------|\n"
            f"|app_db|{reader}|{writer}|{owner}|\n"
        )

    def test_reader_only_is_read_only(self):
        self.assertEqual(sql_login.role_result(self.table(1, 0, 0), "app_db"), "read-only")

    def test_reader_not_required(self):
        self.assertEqual(sql_login.role_result(self.table(0, 0, 0), "app_db"), "read-only")

    def test_writer_or_owner_can_write(self):
        self.assertEqual(sql_login.role_result(self.table(1, 1, 0), "app_db"), "can-write")
        self.assertEqual(sql_login.role_result(self.table(1, 0, 1), "app_db"), "can-write")

    def test_missing_row(self):
        self.assertEqual(sql_login.role_result("|x|\n|-|\n", "app_db"), "missing")

    def test_a_lone_name_stops(self):
        # SQL Server runs a lone name at the start of a batch as a procedure call.
        for sql in ("[usp_Purge]", '"usp_Purge"', "SELECT 1;\n[usp_Purge]", "SELECT 1\n\n[dbo].[usp_Purge]"):
            reason = sql_login.refuse_reason(sql)
            self.assertIsNotNone(reason, sql)
            self.assertIn("Only SELECT and WITH", reason)

    def test_next_value_for_stops(self):
        reason = sql_login.refuse_reason("SELECT NEXT VALUE FOR dbo.OrderNumbers;")
        self.assertEqual(reason, "the query contains NEXT VALUE FOR. Only SELECT and WITH are allowed.")
        self.assertIsNone(sql_login.refuse_reason("SELECT 'next value for' AS words;"))


class ApostropheTests(unittest.TestCase):
    def test_doubled_apostrophe_passes(self):
        self.assertIsNone(sql_login.refuse_reason("SELECT 1 FROM dbo.Customer WHERE Name = N'O''Brien';"))

    def test_single_apostrophe_stops_with_the_hint(self):
        reason = sql_login.refuse_reason("SELECT 1 FROM dbo.Customer WHERE Name = N'O'Brien';")
        self.assertEqual(reason, sql_login.UNCLOSED_MESSAGE)
        self.assertIn("N'O''Brien'", reason)


class SavedQueriesPathTests(unittest.TestCase):
    def test_next_to_a_named_model(self):
        paths = sql_login.config_paths(Path("/tmp/settings"))
        found = sql_login.queries_path({"model_path": "/work/models/data-model.md"}, paths)
        self.assertEqual(found, Path("/work/models/data-model.saved-queries.md"))

    def test_next_to_the_default_model(self):
        paths = sql_login.config_paths(Path("/tmp/settings"))
        found = sql_login.queries_path(sql_login.empty_setup(), paths)
        self.assertEqual(found, Path("/tmp/settings/data-model.saved-queries.md"))

    def test_paths_prints_queries_path(self):
        with tempfile.TemporaryDirectory() as root:
            paths = sql_login.config_paths(Path(root))
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                sql_login.print_paths(paths)
            self.assertIn(f"queries_path={Path(root) / 'data-model.saved-queries.md'}", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
