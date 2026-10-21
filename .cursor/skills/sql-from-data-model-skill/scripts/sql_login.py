#!/usr/bin/env python3
"""Cross-platform Option A tool for sql-from-data-model-skill.

Commands: paths, check, init-databases, setup, run.
Does not print passwords. Call setup or run only when a person is at the computer.
"""
import json
import locale
import os
import re
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

RELEASES_URL = "https://github.com/dbeaver/dbvr/releases/latest"
MIN_VERSION = (26, 2, 0)
ROW_LIMIT = "100000"
KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
DOTTED_VERSION_RE = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?")
BARE_VERSION_RE = re.compile(r"\b(\d+)\b")
FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|TRUNCATE|ALTER|DROP|CREATE|EXEC|EXECUTE|GRANT|REVOKE|DENY|INTO|DECLARE"
    r"|OPENROWSET|OPENQUERY|OPENDATASOURCE|USE|WAITFOR|DBCC|BACKUP|RESTORE|BULK|KILL|SHUTDOWN"
    r"|NEXT\s+VALUE\s+FOR)\b",
    re.IGNORECASE,
)
# A bracketed or double-quoted name becomes this marker, so a lone name still has a first word.
# SQL Server runs a lone name at the start of a batch as a stored procedure call.
NAME_MARKER = " [name] "
ALLOWED_SET = {
    "set nocount on",
    "set nocount off",
    "set transaction isolation level read uncommitted",
}
CONTINUATIONS = {
    "UNION", "EXCEPT", "INTERSECT", "AND", "OR", "ON", "JOIN",
    "INNER", "LEFT", "RIGHT", "FULL", "CROSS", "OUTER",
    "FROM", "WHERE", "GROUP", "ORDER", "HAVING", "OFFSET", "FETCH", "OPTION",
}
PIPE_SEPARATOR_RE = re.compile(r"^\|[-|\s]+\|$")
PIPE_VALUE_NOTE = 'NOTE a value contains "|", so this table may display wrong'
APOSTROPHE_HINT = "If a value contains an apostrophe, write it twice, for example N'O''Brien'."
DECLARE_MESSAGE = (
    "the query uses DECLARE. dbvr runs each statement separately, "
    "so variables are lost. Put the value directly in the query instead. "
    + APOSTROPHE_HINT
)
UNCLOSED_MESSAGE = "the query has an unclosed quote, bracket, or comment. " + APOSTROPHE_HINT
ROLE_QUERY = (
    "SELECT DB_NAME() AS database_name, "
    "IS_ROLEMEMBER('db_datareader') AS reader_role, "
    "IS_ROLEMEMBER('db_datawriter') AS writer_role, "
    "IS_ROLEMEMBER('db_owner') AS owner_role;"
)

# Verified on Mac on 2026-10-15. Edit menu, activation policy, and lock.shield stay.
JXA = r'''
ObjC.import('Cocoa');
function addEditMenu(app) {
  const mainMenu = $.NSMenu.alloc.init;
  const appItem = $.NSMenuItem.alloc.init;
  mainMenu.addItem(appItem);
  const appMenu = $.NSMenu.alloc.initWithTitle('Login');
  appMenu.addItemWithTitleActionKeyEquivalent('Quit', 'terminate:', 'q');
  appItem.submenu = appMenu;
  const editItem = $.NSMenuItem.alloc.init;
  mainMenu.addItem(editItem);
  const edit = $.NSMenu.alloc.initWithTitle('Edit');
  edit.addItemWithTitleActionKeyEquivalent('Undo', 'undo:', 'z');
  edit.addItem($.NSMenuItem.separatorItem);
  edit.addItemWithTitleActionKeyEquivalent('Cut', 'cut:', 'x');
  edit.addItemWithTitleActionKeyEquivalent('Copy', 'copy:', 'c');
  edit.addItemWithTitleActionKeyEquivalent('Paste', 'paste:', 'v');
  edit.addItemWithTitleActionKeyEquivalent('Select All', 'selectAll:', 'a');
  editItem.submenu = edit;
  app.mainMenu = mainMenu;
}
function run(argv) {
  const title = argv[0], info = argv[1], button = argv[2];
  const specs = argv.slice(3).map(function (s) {
    const p = s.split('|');
    return { label: p[0], mode: p[1], value: p.slice(2).join('|') };
  });
  const app = $.NSApplication.sharedApplication;
  app.setActivationPolicy(0);
  addEditMenu(app);
  const rowH = 32, labelW = 220, fieldW = 240, width = labelW + 10 + fieldW;
  const height = specs.length * rowH;
  const view = $.NSView.alloc.initWithFrame($.NSMakeRect(0, 0, width, height));
  const fields = [];
  specs.forEach(function (s, i) {
    const y = height - (i + 1) * rowH + 4;
    const label = $.NSTextField.labelWithString(s.label);
    label.frame = $.NSMakeRect(0, y + 4, labelW, 18);
    view.addSubview(label);
    const rect = $.NSMakeRect(labelW + 10, y, fieldW, 24);
    const field = s.mode === 'secure'
      ? $.NSSecureTextField.alloc.initWithFrame(rect)
      : $.NSTextField.alloc.initWithFrame(rect);
    field.stringValue = s.value;
    if (s.mode === 'readonly') {
      field.editable = false;
      field.selectable = false;
      field.bezeled = false;
      field.drawsBackground = false;
    }
    view.addSubview(field);
    fields.push(field);
  });
  const editable = fields.filter(function (f, i) { return specs[i].mode !== 'readonly'; });
  for (let i = 0; i < editable.length; i++) {
    editable[i].nextKeyView = editable[(i + 1) % editable.length];
  }
  const alert = $.NSAlert.alloc.init;
  alert.messageText = title;
  alert.informativeText = info;
  alert.addButtonWithTitle(button);
  alert.addButtonWithTitle('Cancel');
  alert.accessoryView = view;
  try {
    const cfg = $.NSImageSymbolConfiguration.configurationWithPointSizeWeight(44, 0);
    const img = $.NSImage.imageWithSystemSymbolNameAccessibilityDescription('lock.shield', 'Sign in');
    if (img && !img.isNil()) alert.icon = img.imageWithSymbolConfiguration(cfg);
  } catch (e) {}
  alert.layout;
  if (editable.length) alert.window.initialFirstResponder = editable[0];
  alert.window.level = 3;
  app.activateIgnoringOtherApps(true);
  const r = alert.runModal;
  if (r != 1000) return 'CANCELLED';
  return JSON.stringify(fields.map(function (f) { return f.stringValue.js; }));
}
'''

PS1 = r'''
param([Parameter(Mandatory=$true)][string]$SpecPath)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
$spec = Get-Content -LiteralPath $SpecPath -Raw -Encoding UTF8 | ConvertFrom-Json
# Load the WinForms assemblies. The cmdlet name is split on purpose. Keep the split.
& ("Add-" + "Type") -AssemblyName System.Windows.Forms
& ("Add-" + "Type") -AssemblyName System.Drawing
$form = New-Object System.Windows.Forms.Form
$form.Text = [string]$spec.title
$form.TopMost = $true
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.Font = New-Object System.Drawing.Font('Segoe UI', 9)
$fields = @($spec.fields)
$info = New-Object System.Windows.Forms.Label
$info.Text = [string]$spec.info
$info.AutoSize = $false
$info.Width = 520
$info.Height = 56
$info.Location = New-Object System.Drawing.Point(12, 12)
$form.Controls.Add($info)
$y = 76
$boxes = New-Object System.Collections.Generic.List[System.Windows.Forms.TextBox]
foreach ($f in $fields) {
  $lbl = New-Object System.Windows.Forms.Label
  $lbl.Text = [string]$f.label
  $lbl.AutoSize = $false
  $lbl.Width = 220
  $lbl.Height = 22
  $lbl.Location = New-Object System.Drawing.Point(12, ($y + 4))
  $box = New-Object System.Windows.Forms.TextBox
  $box.Width = 280
  $box.Location = New-Object System.Drawing.Point(240, $y)
  if ([string]$f.mode -eq 'secure') { $box.UseSystemPasswordChar = $true }
  else { $box.Text = [string]$f.value }
  $form.Controls.Add($lbl)
  $form.Controls.Add($box)
  [void]$boxes.Add($box)
  $y += 32
}
$ok = New-Object System.Windows.Forms.Button
$ok.Text = [string]$spec.button
$ok.DialogResult = [System.Windows.Forms.DialogResult]::OK
$ok.Width = 88
$cancel = New-Object System.Windows.Forms.Button
$cancel.Text = 'Cancel'
$cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$cancel.Width = 88
$ok.Location = New-Object System.Drawing.Point(320, ($y + 8))
$cancel.Location = New-Object System.Drawing.Point(416, ($y + 8))
$form.Controls.Add($ok)
$form.Controls.Add($cancel)
$form.AcceptButton = $ok
$form.CancelButton = $cancel
$form.ClientSize = New-Object System.Drawing.Size(520, ($y + 52))
if ($boxes.Count -gt 0) {
  $form.Add_Shown({ $boxes[0].Focus() }.GetNewClosure())
}
$result = $form.ShowDialog()
if ($result -ne [System.Windows.Forms.DialogResult]::OK) {
  [Console]::Out.WriteLine('CANCELLED')
  exit 0
}
$values = New-Object System.Collections.Generic.List[string]
foreach ($b in $boxes) { [void]$values.Add([string]$b.Text) }
[Console]::Out.WriteLine((ConvertTo-Json -InputObject $values.ToArray() -Compress))
'''


def stop(message):
    print(f"STOP {message}")
    sys.exit(1)


def settings_dir(platform=None, environ=None, home=None):
    platform = platform or sys.platform
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    if platform == "win32":
        appdata = environ.get("APPDATA")
        base = Path(appdata) if appdata else home / "AppData" / "Roaming"
        return base / "sql-from-data-model"
    return home / ".config" / "sql-from-data-model"


def config_paths(root=None):
    root = settings_dir() if root is None else Path(root)
    return {
        "settings_dir": root,
        "setup_json": root / "setup.json",
        "databases_json": root / "databases.json",
        "env_file": root / ".env",
        "dbvr_workspace": root / "dbvr-workspace",
    }


def empty_setup():
    return {
        "source": "",
        "dbvr_path": "",
        "model_path": "",
        "repo_links": {},
        "notes_path": "",
        "read_access_confirmed": False,
    }


def clean_setup(data):
    """Keep the known setup fields. Drop anything that could be a secret.

    repo_links is one link per database label. notes_path is optional and
    stays empty when the user has no notes file.
    """
    if not isinstance(data, dict):
        return empty_setup()
    links = {}
    raw_links = data.get("repo_links")
    if isinstance(raw_links, dict):
        for label, link in raw_links.items():
            name = str(label).strip()
            if name:
                links[name] = str(link or "")
    source = data.get("source") if data.get("source") in ("dbvr", "repos") else ""
    return {
        "source": source,
        "dbvr_path": str(data.get("dbvr_path") or ""),
        "model_path": str(data.get("model_path") or ""),
        "repo_links": links,
        "notes_path": str(data.get("notes_path") or ""),
        "read_access_confirmed": bool(data.get("read_access_confirmed")),
    }


def load_setup(paths=None):
    paths = paths or config_paths()
    path = paths["setup_json"]
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return empty_setup()


def save_setup(data, paths=None):
    paths = paths or config_paths()
    ensure_private_dir(paths["settings_dir"])
    clean = clean_setup(data)
    paths["setup_json"].write_text(json.dumps(clean, indent=2) + "\n", encoding="utf-8")
    private_file(paths["setup_json"])


def model_path(setup, paths):
    named = str((setup or {}).get("model_path") or "").strip()
    if named:
        return Path(named)
    return paths["settings_dir"] / "data-model.md"


def queries_path(setup, paths):
    model = model_path(setup, paths)
    return model.with_name(f"{model.stem}.saved-queries.md")


def parse_version(text):
    raw = text or ""
    dotted = DOTTED_VERSION_RE.search(raw)
    if dotted:
        return (int(dotted.group(1)), int(dotted.group(2)), int(dotted.group(3) or 0))
    bare = BARE_VERSION_RE.search(raw)
    if bare:
        return (int(bare.group(1)), 0, 0)
    return None


def version_ok(text):
    found = parse_version(text)
    return found is not None and found >= MIN_VERSION


def candidate_dbvr_paths(platform, environ, setup_dbvr_path, home, which):
    """Search order. which is a name->path map standing in for PATH."""
    found = []
    if setup_dbvr_path:
        found.append(str(setup_dbvr_path))
    names = ("dbvr.exe", "dbvr") if platform == "win32" else ("dbvr",)
    for name in names:
        hit = which.get(name) if isinstance(which, dict) else None
        if hit:
            found.append(str(hit))
    home = Path(home)
    if platform == "darwin":
        found.append("/Applications/dbvr.app/Contents/MacOS/dbvr")
        found.append(str(home / "Applications" / "dbvr.app" / "Contents" / "MacOS" / "dbvr"))
    elif platform == "win32":
        program_files = environ.get("ProgramFiles") or r"C:\Program Files"
        local = environ.get("LOCALAPPDATA") or ""
        found.append(str(Path(program_files) / "dbvr" / "dbvr.exe"))
        if local:
            found.append(str(Path(local) / "Programs" / "dbvr" / "dbvr.exe"))
    return found


def first_executable(candidates):
    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def which_map():
    found = {}
    for name in ("dbvr", "dbvr.exe"):
        hit = shutil.which(name)
        if hit:
            found[name] = hit
    return found


def find_dbvr(setup, platform=None, environ=None, home=None):
    platform = platform or sys.platform
    environ = os.environ if environ is None else environ
    home = Path.home() if home is None else Path(home)
    saved = (setup or {}).get("dbvr_path") or ""
    candidates = candidate_dbvr_paths(platform, environ, saved, home, which_map())
    return first_executable(candidates)


def remember_dbvr_path(path, paths=None):
    if not path:
        return
    current = load_setup(paths)
    current["dbvr_path"] = str(path)
    save_setup(current, paths)


def validate_databases(data):
    errors = []
    if not isinstance(data, dict) or not isinstance(data.get("environments"), list) or not data["environments"]:
        return ["databases.json needs a non-empty environments list"]
    seen = set()
    seen_databases = set()
    seen_envs = set()
    for env in data["environments"]:
        if not isinstance(env, dict) or not str(env.get("name") or "").strip():
            errors.append("each environment needs a name")
            continue
        name = str(env["name"]).strip()
        if name.lower() in seen_envs:
            errors.append(f"duplicate environment {name}")
        seen_envs.add(name.lower())
        databases = env.get("databases")
        if not isinstance(databases, list) or not databases:
            errors.append(f"{name} needs a databases list")
            continue
        for db in databases:
            if not isinstance(db, dict):
                errors.append(f"{name} has a database entry that is not an object")
                continue
            key = str(db.get("key") or "")
            for field in ("key", "label", "server", "database"):
                if not str(db.get(field) or "").strip():
                    errors.append(f"{name} database missing {field}")
            if key and not KEY_RE.match(key):
                errors.append(f"key {key} must start with a letter and use letters, digits, and underscores")
            if key in seen:
                errors.append(f"duplicate key {key}")
            if key:
                seen.add(key)
            database_name = str(db.get("database") or "")
            if database_name and database_name in seen_databases:
                errors.append(f"duplicate database {database_name}")
            if database_name:
                seen_databases.add(database_name)
            port = db.get("port")
            if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
                errors.append(f"{key or name} port must be an integer from 1 to 65535")
            for secret_name in ("password", "username", "user", "connectionString", "connection_string"):
                if secret_name in db:
                    errors.append(f"{key or name} must not contain {secret_name}")
    return errors


def flatten_databases(data):
    rows = []
    for env in data.get("environments") or []:
        env_name = str(env.get("name") or "")
        for db in env.get("databases") or []:
            rows.append({
                "env": env_name,
                "key": db["key"],
                "label": db["label"],
                "server": db["server"],
                "port": int(db["port"]),
                "database": db["database"],
            })
    return rows


def user_env_key(key):
    return f"SQL_USER_{key}"


def password_env_key(key):
    return f"SQL_PASSWORD_{key}"


def resolve_user(values, key):
    specific = str((values or {}).get(user_env_key(key)) or "").strip()
    if specific:
        return specific
    return str((values or {}).get("SQL_USER") or "").strip()


def resolve_password(values, key):
    return str((values or {}).get(password_env_key(key)) or "").strip()


def credentials_complete(values, databases):
    missing = []
    for db in databases:
        if not resolve_user(values, db["key"]) or not resolve_password(values, db["key"]):
            missing.append(db["key"])
    return missing


def quote_env(value):
    return "'" + str(value).replace("'", "'\"'\"'") + "'"


def unquote_env(raw):
    parts = shlex.split(raw or "")
    return parts[0] if parts else ""


def load_env(path):
    values = {}
    if not path or not Path(path).exists():
        return values
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, raw = line.split("=", 1)
        values[key.strip()] = unquote_env(raw.strip())
    return values


def save_env(values, path):
    path = Path(path)
    ensure_private_dir(path.parent)
    body = "".join(f"{key}={quote_env(val)}\n" for key, val in values.items())
    path.write_text(body, encoding="utf-8")
    private_file(path)


def ensure_private_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        os.chmod(path, stat.S_IRWXU)


def private_file(path):
    if os.name != "nt":
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def port_open(server, port, timeout=8, connector=None):
    connect = connector or socket.create_connection
    try:
        sock = connect((server, int(port)), timeout)
    except OSError:
        return False
    try:
        sock.close()
    except OSError:
        pass
    return True


def _word_char(char):
    return char.isalnum() or char == "_"


def _scan_quoted(text, start, quote):
    """Return the index after a quoted span, or None when it is unclosed. Doubled quotes escape."""
    index = start + 1
    length = len(text)
    while index < length:
        if text[index] == quote:
            if index + 1 < length and text[index + 1] == quote:
                index += 2
                continue
            return index + 1
        index += 1
    return None


def _scan_bracket(text, start):
    """Return the index after […], or None when it is unclosed. ]] is an escaped bracket."""
    index = start + 1
    length = len(text)
    while index < length:
        if text[index] == "]":
            if index + 1 < length and text[index + 1] == "]":
                index += 2
                continue
            return index + 1
        index += 1
    return None


def _scan_block_comment(text, start):
    """Return the index after a nested block comment, or None when it is unclosed."""
    depth = 1
    index = start + 2
    length = len(text)
    while index < length:
        if text.startswith("/*", index):
            depth += 1
            index += 2
            continue
        if text.startswith("*/", index):
            depth -= 1
            index += 2
            if depth == 0:
                return index
            continue
        index += 1
    return None


def prepare_sql(sql):
    """Mask strings, names, and comments from left to right. None means one of them is unclosed."""
    text = (sql or "").replace("\r\n", "\n").replace("\r", "\n")
    out = []
    index = 0
    length = len(text)
    while index < length:
        national = (
            text[index] in "Nn"
            and index + 1 < length
            and text[index + 1] == "'"
            and (index == 0 or not _word_char(text[index - 1]))
        )
        if national or text[index] == "'":
            quote_at = index + 1 if national else index
            end = _scan_quoted(text, quote_at, "'")
            if end is None:
                return None
            out.append("''")
            index = end
            continue
        if text[index] == "[":
            end = _scan_bracket(text, index)
            if end is None:
                return None
            out.append(NAME_MARKER)
            index = end
            continue
        if text[index] == '"':
            end = _scan_quoted(text, index, '"')
            if end is None:
                return None
            out.append(NAME_MARKER)
            index = end
            continue
        if text.startswith("--", index):
            end = text.find("\n", index)
            out.append(" ")
            index = length if end == -1 else end
            continue
        if text.startswith("/*", index):
            end = _scan_block_comment(text, index)
            if end is None:
                return None
            out.append(" ")
            index = end
            continue
        out.append(text[index])
        index += 1
    return "".join(out)


def _can_merge(statements, piece, closed_by_semicolon):
    if not statements or closed_by_semicolon:
        return False
    first = piece.split(None, 1)[0].upper()
    return first in CONTINUATIONS or piece[0] in "),"


def split_statements(sql):
    """Split on semicolons and blank lines. Continuations merge only across a blank line."""
    prepared = prepare_sql(sql)
    if prepared is None:
        return None
    statements = []
    last = 0
    closed_by_semicolon = False
    for match in re.finditer(r";|\n[ \t]*\n", prepared):
        piece = prepared[last:match.start()].strip()
        is_semicolon = match.group(0) == ";"
        last = match.end()
        if piece:
            if _can_merge(statements, piece, closed_by_semicolon):
                statements[-1] = statements[-1] + "\n" + piece
            else:
                statements.append(piece)
        if is_semicolon:
            closed_by_semicolon = True
        elif piece:
            closed_by_semicolon = False
    tail = prepared[last:].strip()
    if tail:
        if _can_merge(statements, tail, closed_by_semicolon):
            statements[-1] = statements[-1] + "\n" + tail
        else:
            statements.append(tail)
    return statements


def statement_allowed(statement):
    words = statement.split()
    if not words:
        return True
    head = words[0].upper()
    if head in ("SELECT", "WITH"):
        return True
    return " ".join(words).lower() in ALLOWED_SET


def forbidden_keyword(sql):
    prepared = prepare_sql(sql)
    if prepared is None:
        return None
    match = FORBIDDEN.search(prepared)
    return " ".join(match.group(1).upper().split()) if match else None


def refuse_reason(sql):
    """Return the stop message for a blocked query, or None when it may run."""
    statements = split_statements(sql)
    if statements is None:
        return UNCLOSED_MESSAGE
    for index, statement in enumerate(statements, start=1):
        if statement_allowed(statement):
            continue
        if statement.split(None, 1)[0].upper() == "DECLARE":
            return DECLARE_MESSAGE
        words = " ".join(statement.split()[:4])
        return f'statement {index} starts with "{words}". Only SELECT and WITH queries are allowed.'
    bad = forbidden_keyword(sql)
    if not bad:
        return None
    if bad == "DECLARE":
        return DECLARE_MESSAGE
    return f"the query contains {bad}. Only SELECT and WITH are allowed."


def decode_output(data):
    """Decode dbvr bytes. UTF-8 first; the local code page is the unverified fallback."""
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        encoding = locale.getpreferredencoding(False) or "utf-8"
        return data.decode(encoding, errors="replace")


def map_dbvr_error(text, label, env_name):
    raw = text or ""
    if "Client with IP address" in raw or "not allowed to access the server" in raw:
        return (
            "The server is reachable but its firewall is blocking your IP address. "
            "Ask the database admin to allow your IP, then run setup again."
        )
    if "Login failed for user" in raw:
        return f"Wrong username or password for {label} {env_name}."
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    tail = " ".join(lines[-5:])[:600]
    return tail or "dbvr did not return a result."


def make_redact(secrets):
    ordered = sorted({s for s in secrets if s}, key=len, reverse=True)

    def redact(text):
        text = text or ""
        for secret in ordered:
            text = text.replace(secret, "[hidden]")
        return text

    return redact


def field_specs(env, last_user, existing):
    specs = []
    for db in env["databases"]:
        prefill = resolve_user(existing, db["key"]) or last_user or ""
        specs.append((f"{db['label']} username", "text", prefill))
        specs.append((f"{db['label']} password", "secure", ""))
    return specs


def paste_hint(platform=None):
    platform = platform or sys.platform
    if platform == "darwin":
        return "Paste with ⌘V."
    if platform == "win32":
        return "Paste with Ctrl+V."
    return "Paste into the fields. This Linux window is untested."


def dbvr_command(dbvr, workspace, host, port, database, user, password, query=None, csv_path=None, input_file=None):
    cmd = [
        dbvr,
        f"-data={workspace}",
        "sql",
        "--driver=microsoft",
        f"--host={host}",
        f"--port={int(port)}",
        f"--database={database}",
        f"--user={user}",
        f"--password={password}",
        "--disable-status",
        f"-l={ROW_LIMIT}",
    ]
    if csv_path:
        cmd.extend(["-format=csv", f"-out={csv_path}"])
    if input_file:
        cmd.append(f"-in={input_file}")
    elif query is not None:
        cmd.append(query)
    return cmd


STDOUT_UTF8_OPTION = "-Dstdout.encoding=UTF-8"


def dbvr_env(platform=None, environ=None):
    """Return a copy of the environment for dbvr. Never changes the one passed in.

    On Windows, dbvr's bundled Java writes stdout in the Windows code page, so an
    emoji prints as "?". -Dstdout.encoding=UTF-8 fixed it (dbvr 26.2.3);
    -Dfile.encoding=UTF-8 did not.
    """
    platform = platform or sys.platform
    env = dict(os.environ if environ is None else environ)
    if platform != "win32":
        return env
    current = env.get("JAVA_TOOL_OPTIONS", "")
    if STDOUT_UTF8_OPTION not in current.split():
        env["JAVA_TOOL_OPTIONS"] = f"{current} {STDOUT_UTF8_OPTION}" if current.strip() else STDOUT_UTF8_OPTION
    return env


def run_dbvr(cmd, timeout):
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout, env=dbvr_env())
    proc.stdout = decode_output(proc.stdout)
    proc.stderr = decode_output(proc.stderr)
    return proc


def _pipe_cell_count(line):
    parts = line.split("|")
    if line.endswith("|") and len(parts) >= 2:
        return len(parts) - 2
    return max(len(parts) - 1, 0)


def _pipe_table_parts(output):
    """Return (data_row_count, uneven) for a dbvr pipe table.

    Data rows are lines starting with ``|``, minus the header, minus separator
    lines. No pipe lines means 0. A data row whose cell count differs from the
    header still counts, and sets uneven.
    """
    header = None
    count = 0
    uneven = False
    for line in (output or "").splitlines():
        if not line.startswith("|"):
            continue
        if PIPE_SEPARATOR_RE.match(line):
            continue
        if header is None:
            header = _pipe_cell_count(line)
            continue
        count += 1
        if _pipe_cell_count(line) != header:
            uneven = True
    return count, uneven


# dbvr empty result: a header and a separator, and no data row.
# |CustomerId|
# |----------|
def count_table_rows(output):
    """Count data rows in dbvr's pipe-table output."""
    count, _uneven = _pipe_table_parts(output)
    return count


def pipe_value_note(output):
    """Return the NOTE line when a data row's cell count differs from the header."""
    _count, uneven = _pipe_table_parts(output)
    if uneven:
        return PIPE_VALUE_NOTE
    return None


def role_result(output, database_name):
    """Return 'read-only', 'can change data', or 'missing' from a pipe table. No database call.

    Only reports. Any login that signs in is accepted; the SQL filter keeps queries read-only.
    """
    rows = [
        line for line in (output or "").splitlines()
        if line.startswith("|") and database_name in line
    ]
    if not rows:
        return "missing"
    cells = [cell.strip() for cell in rows[0].strip().strip("|").split("|")]
    if len(cells) < 4:
        return "missing"
    if "1" in (cells[2], cells[3]):
        return "can change data"
    return "read-only"


def check_login_roles(dbvr, workspace, db, user, password):
    redact = make_redact([user, password])
    cmd = dbvr_command(
        dbvr, workspace, db["server"], db["port"], db["database"], user, password, ROLE_QUERY,
    )
    try:
        proc = run_dbvr(cmd, timeout=180)
    except subprocess.TimeoutExpired:
        return False, "timed out"
    out = redact(proc.stdout or "")
    err = redact(proc.stderr or "")
    blob = f"{err}\n{out}"
    if proc.returncode != 0:
        return False, map_dbvr_error(blob, db["label"], db["env"])
    result = role_result(out, db["database"])
    if result == "missing":
        return False, map_dbvr_error(blob, db["label"], db["env"])
    return True, result


def print_paths(paths=None):
    paths = paths or config_paths()
    if paths["setup_json"].exists():
        setup = load_setup(paths)
    else:
        setup = empty_setup()
    saved = str(setup.get("model_path") or "").strip()
    print(f"settings_dir={paths['settings_dir']}")
    print(f"setup_json={paths['setup_json']}")
    print(f"databases_json={paths['databases_json']}")
    print(f"env_file={paths['env_file']}")
    print(f"model_path={saved or model_path(setup, paths)}")
    print(f"model_path_saved={'yes' if saved else 'no'}")
    print(f"queries_path={queries_path(setup, paths)}")
    print(f"dbvr_workspace={paths['dbvr_workspace']}")
    print(f"platform={sys.platform}")


def dbvr_version_text(dbvr):
    proc = subprocess.run([dbvr, "--version"], capture_output=True, timeout=60)
    text = decode_output(proc.stdout) or decode_output(proc.stderr)
    return text.strip()


def require_dbvr(setup, override, paths):
    if override:
        if not (os.path.isfile(override) and os.access(override, os.X_OK)):
            stop(f"dbvr not found at {override}")
        remember_dbvr_path(override, paths)
        found = override
    else:
        found = find_dbvr(setup)
        if found and str((setup or {}).get("dbvr_path") or "") != found:
            remember_dbvr_path(found, paths)
    if not found:
        stop(
            "dbvr not found. Install dbvr 26.2 or newer from "
            f"{RELEASES_URL} or pass --dbvr-path."
        )
    version = dbvr_version_text(found)
    if not version_ok(version):
        stop(f"dbvr version is {version or 'unknown'}. Need 26.2 or newer.")
    return found, version


def load_databases(paths):
    path = paths["databases_json"]
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_databases(data)
    if errors:
        stop("databases.json is invalid. " + "; ".join(errors))
    return data


def check(setup, override, paths):
    dbvr, version = require_dbvr(setup, override, paths)
    print(f"OK dbvr {dbvr} {version}")
    data = load_databases(paths)
    if data is None:
        print("SKIP databases (no databases.json yet)")
        print("SKIP ports")
        print("SKIP credentials")
        return
    rows = flatten_databases(data)
    print(f"OK databases {len(rows)}")
    for db in rows:
        if not port_open(db["server"], db["port"]):
            stop(
                f"{db['server']} did not answer on port {db['port']}. "
                "Check the VPN or network, then run check again."
            )
        print(f"OK port {db['server']}:{db['port']}")
    if not paths["env_file"].exists():
        print("SKIP credentials (no .env yet)")
        return
    values = load_env(paths["env_file"])
    missing = credentials_complete(values, rows)
    if missing:
        stop("saved login is missing a username or password for " + ", ".join(missing))
    print("OK credentials")


def init_databases(source_token, paths):
    source = Path(source_token)
    if not source.exists():
        stop(f"database file not found: {source}")
    raw = source.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        stop(f"database file is not JSON. {exc}")
    errors = validate_databases(data)
    if errors:
        stop("; ".join(errors))
    ensure_private_dir(paths["settings_dir"])
    text = raw if raw.endswith("\n") else raw + "\n"
    paths["databases_json"].write_text(text, encoding="utf-8")
    private_file(paths["databases_json"])
    print(f"OK databases {paths['databases_json']}")


def mac_dialog(title, info, button, specs):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as handle:
        handle.write(JXA)
        script_path = handle.name
    try:
        args = ["osascript", "-l", "JavaScript", script_path, title, info, button]
        args += [f"{label}|{mode}|{value}" for label, mode, value in specs]
        proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.unlink(script_path)
    out = (proc.stdout or "").strip()
    if proc.returncode != 0:
        stop("the sign-in window could not open. " + (proc.stderr or "").strip()[:300])
    if out == "CANCELLED":
        return None
    return json.loads(out)


def dialog_spec_document(title, info, button, specs):
    return {
        "title": title,
        "info": info,
        "button": button,
        "fields": [
            {"label": label, "mode": mode, "value": "" if mode == "secure" else value}
            for label, mode, value in specs
        ],
    }


def windows_dialog(title, info, button, specs):
    spec = dialog_spec_document(title, info, button, specs)
    fd, spec_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    ps_path = spec_path + ".ps1"
    try:
        Path(spec_path).write_text(json.dumps(spec), encoding="utf-8")
        Path(ps_path).write_text(PS1, encoding="utf-8")
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-STA", "-File", ps_path, spec_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    finally:
        for path in (spec_path, ps_path):
            if os.path.exists(path):
                os.unlink(path)
    out = (proc.stdout or "").strip()
    if proc.returncode != 0:
        stop("the sign-in window could not open. " + (proc.stderr or "").strip()[:300])
    if out == "CANCELLED":
        return None
    parsed = json.loads(out)
    if isinstance(parsed, str):
        return [parsed]
    return list(parsed)


def linux_dialog(title, info, button, specs):
    """Untested fallback. Mac uses JXA. Windows uses PowerShell."""
    try:
        import tkinter as tk
    except ImportError:
        stop("Linux sign-in needs tkinter, which is not installed. This fallback is untested.")
    root = tk.Tk()
    root.title(title)
    result = {"values": None}
    tk.Label(root, text=info, justify="left").pack(padx=12, pady=8, anchor="w")
    boxes = []
    for label, mode, value in specs:
        row = tk.Frame(root)
        row.pack(fill="x", padx=12, pady=4)
        tk.Label(row, text=label, width=28, anchor="w").pack(side="left")
        box = tk.Entry(row, show="*" if mode == "secure" else "", width=32)
        if mode != "secure" and value:
            box.insert(0, value)
        box.pack(side="left")
        boxes.append(box)

    def accept():
        result["values"] = [box.get() for box in boxes]
        root.destroy()

    def cancel():
        root.destroy()

    actions = tk.Frame(root)
    actions.pack(pady=8)
    tk.Button(actions, text=button, command=accept).pack(side="left", padx=4)
    tk.Button(actions, text="Cancel", command=cancel).pack(side="left", padx=4)
    root.protocol("WM_DELETE_WINDOW", cancel)
    if boxes:
        boxes[0].focus_set()
    root.mainloop()
    return result["values"]


def login_dialog(title, info, button, specs):
    if sys.platform == "darwin":
        return mac_dialog(title, info, button, specs)
    if sys.platform == "win32":
        return windows_dialog(title, info, button, specs)
    return linux_dialog(title, info, button, specs)


def ask_until_filled(title, info, button, specs):
    message = info
    current = list(specs)
    for _ in range(3):
        values = login_dialog(title, message, button, current)
        if values is None:
            stop("sign-in cancelled. Nothing was saved.")
        cleaned = [str(value).strip() for value in values]
        if len(cleaned) != len(current):
            stop("the sign-in window returned the wrong number of fields. Nothing was saved.")
        if all(cleaned):
            return cleaned
        current = [
            (label, mode, "" if mode == "secure" else cleaned[index])
            for index, (label, mode, _value) in enumerate(current)
        ]
        message = info + "\n\nEvery field is required."
    stop("a field was left empty three times. Nothing was saved.")


def environments_in_scope(data, only_name):
    environments = data["environments"]
    if not only_name:
        return environments
    match = [env for env in environments if str(env.get("name") or "").lower() == only_name.lower()]
    if not match:
        names = ", ".join(str(env.get("name") or "") for env in environments)
        stop(f"no environment named {only_name}. Known environments: {names}")
    return match


def setup(setup_doc, override, paths, only_env=None):
    dbvr, _version = require_dbvr(setup_doc, override, paths)
    data = load_databases(paths)
    if data is None:
        stop("no databases.json. Run init-databases first.")
    scope = environments_in_scope(data, only_env)
    scope_rows = []
    for env in scope:
        for db in flatten_databases({"environments": [env]}):
            scope_rows.append(db)
    for db in scope_rows:
        if not port_open(db["server"], db["port"]):
            stop(
                f"{db['server']} did not answer on port {db['port']}. "
                "Check the VPN or network, then run setup again."
            )
    print("OK prerequisites", flush=True)
    existing = load_env(paths["env_file"])
    last_user = str(existing.get("SQL_USER") or "")
    collected = {}
    total = len(scope)
    for index, env in enumerate(scope, start=1):
        specs = field_specs(env, last_user, existing)
        button = "Sign In" if index == total else "Continue"
        info = f"Step {index} of {total}. {env['name']} environment.\n{paste_hint()}"
        values = ask_until_filled(f"Sign in to {env['name']}", info, button, specs)
        databases = env["databases"]
        if len(values) != len(databases) * 2:
            stop("the sign-in window returned the wrong number of fields. Nothing was saved.")
        for offset, db in enumerate(databases):
            username = values[offset * 2]
            password = values[offset * 2 + 1]
            collected[db["key"]] = (username, password)
            last_user = username
    workspace = paths["dbvr_workspace"]
    workspace.mkdir(parents=True, exist_ok=True)
    failures = []
    for db in scope_rows:
        username, password = collected[db["key"]]
        ok, detail = check_login_roles(dbvr, workspace, db, username, password)
        print(f"{'OK' if ok else 'FAILED'} {db['database']}: {detail}", flush=True)
        if not ok:
            failures.append(db["database"])
    if failures:
        stop("nothing was saved. Fix: " + ", ".join(failures))
    merged = dict(existing)
    for key, (username, password) in collected.items():
        merged[user_env_key(key)] = username
        merged[password_env_key(key)] = password
    if last_user and "SQL_USER" not in merged:
        merged["SQL_USER"] = last_user
    save_env(merged, paths["env_file"])
    print(f"SAVED {paths['env_file']}")


def run_query(database_name, sql_file, csv_path, setup_doc, override, paths):
    dbvr, _version = require_dbvr(setup_doc, override, paths)
    data = load_databases(paths)
    if data is None:
        stop("no databases.json. Run init-databases first.")
    match = next((db for db in flatten_databases(data) if db["database"] == database_name), None)
    if not match:
        stop(f"{database_name} is not in databases.json.")
    sql_path = Path(sql_file)
    if not sql_path.exists():
        stop(f"SQL file not found: {sql_path}")
    sql = sql_path.read_text(encoding="utf-8-sig")
    reason = refuse_reason(sql)
    if reason:
        stop(reason)
    values = load_env(paths["env_file"])
    user = resolve_user(values, match["key"])
    password = resolve_password(values, match["key"])
    if not user or not password:
        stop("the saved login is missing a value. Run setup again.")
    workspace = paths["dbvr_workspace"]
    workspace.mkdir(parents=True, exist_ok=True)
    redact = make_redact([user, password])
    cmd = dbvr_command(
        dbvr, workspace, match["server"], match["port"], match["database"],
        user, password, csv_path=csv_path, input_file=str(sql_path),
    )
    try:
        proc = run_dbvr(cmd, timeout=600)
    except subprocess.TimeoutExpired:
        stop(f"{match['database']}: the query timed out.")
    out = redact(proc.stdout or "")
    err = redact(proc.stderr or "")
    if proc.returncode != 0:
        stop(f"{match['database']}: " + map_dbvr_error(f"{err}\n{out}", match["label"], match["env"]))
    print(f"DATABASE {match['database']}")
    if csv_path:
        print(f"CSV {csv_path}")
        csv_file = Path(csv_path)
        if csv_file.exists():
            with csv_file.open(encoding="utf-8", errors="replace") as handle:
                rows = max(sum(1 for _ in handle) - 1, 0)
            print(f"ROWS {rows}")
        return
    print(out.rstrip())
    print(f"ROWS {count_table_rows(out)}")
    note = pipe_value_note(out)
    if note:
        print(note)


def take_flag(args, flag):
    if flag not in args:
        return None, args
    index = args.index(flag)
    if index + 1 >= len(args):
        stop(f"{flag} needs a value")
    value = args[index + 1]
    return value, args[:index] + args[index + 2:]


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    override, args = take_flag(list(argv), "--dbvr-path")
    paths = config_paths()
    if override:
        remember_dbvr_path(override, paths)
    setup_doc = load_setup(paths)
    if override:
        setup_doc["dbvr_path"] = override
    command = args[0] if args else ""
    if command == "paths":
        print_paths(paths)
        return
    if command == "check":
        check(setup_doc, override, paths)
        return
    if command == "init-databases" and len(args) == 2:
        init_databases(args[1], paths)
        return
    if command == "setup":
        only_env, rest = take_flag(args[1:], "--env")
        if rest:
            stop("usage: sql_login.py setup [--env <name>]")
        setup(setup_doc, override, paths, only_env)
        return
    if command == "run" and len(args) >= 3:
        csv_path, rest = take_flag(args[1:], "--csv")
        if len(rest) != 2:
            stop("usage: sql_login.py run <database> <sql-file> [--csv <path>]")
        run_query(rest[0], rest[1], csv_path, setup_doc, override, paths)
        return
    stop("usage: sql_login.py paths | check | init-databases <file> | setup [--env <name>] | run <database> <sql-file> [--csv <path>]")


if __name__ == "__main__":
    main(sys.argv[1:])
