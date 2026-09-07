// Leopard Language extension — run/check/build commands for .lep files.
//
// Syntax highlighting, editor behaviours and snippets are entirely
// declarative (package.json + the grammar + language-configuration.json);
// none of them need this file. Everything here exists only to drive the
// `leopard` command and turn its errors into entries in the Problems panel.

const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');

/** `leopard check` reports `<path>:<line>: <message>` — it prefixes the file
 *  precisely so an editor knows what the line number belongs to. */
const CHECK_RE = /^(.*?):(\d+):\s+(.*)$/;

/** `leopard run` reports LeopardError's own format, `Line <n>: <message>`
 *  (leopard_lang/errors.py), which names no file and no column. Diagnostics
 *  from a run are therefore pinned to the file that was run. */
const RUN_RE = /^Line (\d+):\s+(.*)$/;

let diagnostics = null;
let output = null;

function config() {
  return vscode.workspace.getConfiguration('leopard');
}

function interpreter() {
  return config().get('interpreterPath', 'leopard') || 'leopard';
}

/** Quote a path for a shell command line (the terminal path). */
function shellQuote(p) {
  if (process.platform === 'win32') return `"${p}"`;
  return `'${p.replace(/'/g, `'\\''`)}'`;
}

async function activeLeopardDocument() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'leopard') {
    vscode.window.showErrorMessage('Leopard: no .lep file is active.');
    return null;
  }
  if (config().get('saveBeforeRun', true) && editor.document.isDirty) {
    await editor.document.save();
  }
  return editor.document;
}

/** Run in the integrated terminal — output appears live, `input()` works, and
 *  a window program gets a normal controlling process. One reused terminal. */
function runInTerminal(doc, args) {
  let term = vscode.window.terminals.find((t) => t.name === 'Leopard');
  if (!term) {
    term = vscode.window.createTerminal({
      name: 'Leopard',
      cwd: path.dirname(doc.fileName),
    });
  }
  term.show(true);
  // Joined from parts rather than interpolated, so an empty args list cannot
  // leave a double space -- collapsing whitespace afterwards would corrupt a
  // quoted path that legitimately contains consecutive spaces.
  const parts = [
    shellQuote(interpreter()),
    ...args.map((a) => (a === doc.fileName ? shellQuote(a) : a)),
  ];
  term.sendText(parts.join(' '));
}

/** Run as a child process — output goes to an Output channel and errors
 *  become squiggles in the editor via the Problems panel. */
function runInOutputChannel(doc, args, label) {
  if (!output) output = vscode.window.createOutputChannel('Leopard');
  output.clear();
  output.show(true);

  const exe = interpreter();
  output.appendLine(`> ${exe} ${args.join(' ')}`);
  output.appendLine('');

  const started = Date.now();
  const child = cp.spawn(exe, args, { cwd: path.dirname(doc.fileName) });

  let stderr = '';
  child.stdout.on('data', (d) => output.append(d.toString()));
  child.stderr.on('data', (d) => {
    const text = d.toString();
    stderr += text;
    output.append(text);
  });

  child.on('error', (err) => reportSpawnError(err, exe));

  child.on('close', (code) => {
    if (!reportMissingSubcommand(stderr, args[0])) {
      publishDiagnostics(doc, stderr);
    }
    output.appendLine('');
    output.appendLine(
      `[${label} exit ${code} in ${((Date.now() - started) / 1000).toFixed(2)}s]`
    );
  });
}

function reportSpawnError(err, exe) {
  if (err.code === 'ENOENT') {
    vscode.window
      .showErrorMessage(
        `Leopard: '${exe}' not found. Run 'pip install -e .' in the Leopard repo, or set leopard.interpreterPath.`,
        'Open Settings'
      )
      .then((choice) => {
        if (choice === 'Open Settings') {
          vscode.commands.executeCommand(
            'workbench.action.openSettings',
            'leopard.interpreterPath'
          );
        }
      });
  } else {
    vscode.window.showErrorMessage(`Leopard: ${err.message}`);
  }
}

/** `leopard check` was added after the first release, so an older install
 *  rejects it at the argument parser. Say so plainly rather than letting
 *  argparse's usage dump land in the Problems panel as a mystery. */
function reportMissingSubcommand(stderr, subcommand) {
  if (subcommand !== 'check') return false;
  if (!/invalid choice: 'check'/.test(stderr)) return false;
  vscode.window.showWarningMessage(
    "Leopard: this install of `leopard` has no `check` subcommand. Update the Leopard package, or use Run instead."
  );
  return true;
}

/** Turn error lines from stderr into editor squiggles.
 *
 *  Two formats reach here: `leopard check` emits `<path>:<line>: <message>`,
 *  while a failing `leopard run` emits LeopardError's own `Line <n>: <message>`
 *  with no path at all. The second is pinned to `doc`, which is correct
 *  because that is the file we asked Leopard to run. */
function publishDiagnostics(doc, stderr) {
  const byFile = new Map();

  const add = (uri, line, message) => {
    // Leopard reports 1-based lines and no column; underline the whole line.
    const lineNo = Math.max(0, parseInt(line, 10) - 1);
    const diag = new vscode.Diagnostic(
      new vscode.Range(lineNo, 0, lineNo, Number.MAX_SAFE_INTEGER),
      message,
      vscode.DiagnosticSeverity.Error
    );
    diag.source = 'leopard';
    const key = uri.toString();
    if (!byFile.has(key)) byFile.set(key, { uri, items: [] });
    byFile.get(key).items.push(diag);
  };

  for (const raw of stderr.split('\n')) {
    const line = raw.trim();
    if (!line) continue;

    const run = RUN_RE.exec(line);
    if (run) {
      add(doc.uri, run[1], run[2]);
      continue;
    }

    const chk = CHECK_RE.exec(line);
    // Guard against a Windows drive letter ("C:\...") being read as the line
    // number, and against ordinary prose that happens to contain a colon.
    if (chk && /^\d+$/.test(chk[2])) {
      const file = chk[1];
      const uri = vscode.Uri.file(
        path.resolve(path.dirname(doc.fileName), file)
      );
      add(uri, chk[2], chk[3]);
    }
  }

  diagnostics.clear();
  for (const { uri, items } of byFile.values()) {
    diagnostics.set(uri, items);
  }
}

/** `leopard check` in the background, for checkOnSave. Reports into the
 *  Problems panel without stealing focus with an Output channel. */
function checkQuietly(doc) {
  const exe = interpreter();
  const child = cp.spawn(exe, ['check', doc.fileName], {
    cwd: path.dirname(doc.fileName),
  });

  let stderr = '';
  child.stderr.on('data', (d) => (stderr += d.toString()));
  // A missing interpreter would fire on every save -- stay silent and let the
  // explicit commands be the ones that complain.
  child.on('error', () => {});
  child.on('close', () => {
    if (/invalid choice: 'check'/.test(stderr)) return;
    publishDiagnostics(doc, stderr);
  });
}

async function run() {
  const doc = await activeLeopardDocument();
  if (!doc) return;
  const args = ['run', doc.fileName];
  if (config().get('runInTerminal', true)) runInTerminal(doc, args);
  else runInOutputChannel(doc, args, 'run');
}

/** Parse-only: never executes the program, so a script that opens dialogs or
 *  writes files stays inert while you are only asking whether it parses. */
async function checkFile() {
  const doc = await activeLeopardDocument();
  if (!doc) return;
  runInOutputChannel(doc, ['check', doc.fileName], 'check');
}

async function buildFile() {
  const doc = await activeLeopardDocument();
  if (!doc) return;
  const outDir = config().get('buildOutputDir', 'dist') || 'dist';
  const name = path.basename(doc.fileName, '.lep');
  runInOutputChannel(
    doc,
    ['build', doc.fileName, '-o', outDir, '-n', name],
    'build'
  );
}

function activate(context) {
  diagnostics = vscode.languages.createDiagnosticCollection('leopard');

  context.subscriptions.push(
    diagnostics,
    vscode.commands.registerCommand('leopard.runFile', run),
    vscode.commands.registerCommand('leopard.checkFile', checkFile),
    vscode.commands.registerCommand('leopard.buildFile', buildFile),

    // A file's errors are stale the moment it is edited.
    vscode.workspace.onDidChangeTextDocument((e) => {
      if (e.document.languageId === 'leopard') {
        diagnostics.delete(e.document.uri);
      }
    }),

    vscode.workspace.onDidSaveTextDocument((doc) => {
      if (doc.languageId === 'leopard' && config().get('checkOnSave', false)) {
        checkQuietly(doc);
      }
    })
  );
}

function deactivate() {
  if (output) output.dispose();
}

module.exports = { activate, deactivate };
