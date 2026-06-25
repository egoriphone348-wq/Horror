#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-обёртка для игры «Подвал Безумия».
Запускает HTTP-сервер с xterm.js-терминалом в браузере.
"""

import sys
import os
import io
import re
import json
import uuid
import time as _time_module
import builtins
import contextlib
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8080))
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GAME_DIR)

# ─── Патчи для веб-режима (до импорта игры) ───────────────────

class _GameOver(Exception):
    pass

_time_module.sleep = lambda _: None
_orig_input = builtins.input
builtins.input = lambda prompt="": ""
_orig_exit = sys.exit
sys.exit = lambda code=0: (_ for _ in ()).throw(_GameOver())

import game as G  # импортируем ПОСЛЕ патчей

# Заменяем clear() на ESC-последовательность очистки xterm
G.clear = lambda: print("\033[2J\033[H", end="", flush=True)

# Jumpscare без паузы на input() 
def _web_jumpscare(text):
    w = 70
    pad = max(0, (w - len(text) - 4) // 2)
    print(f"\r\n\033[41m\033[97m\033[1m{' ' * pad}  {text}  {' ' * pad}\033[0m\r\n")
G.jumpscare = _web_jumpscare

# ─── Хранилище сессий ─────────────────────────────────────────

sessions: dict = {}   # session_id -> GameState

def _new_session() -> tuple:
    sid = str(uuid.uuid4())
    state = G.GameState()
    sessions[sid] = state
    return sid, state

def _get_session(sid: str):
    return sessions.get(sid)

# ─── Захват вывода ────────────────────────────────────────────

def _capture(fn, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            result = fn(*args, **kwargs)
        except (_GameOver, SystemExit):
            result = None
        except Exception:
            result = None
    return buf.getvalue(), result

def _room_view(state) -> str:
    out, _ = _capture(lambda: (G.show_hud(state), G.show_room(state)))
    return out

def _process(state, raw_cmd: str):
    """Обрабатывает команду, двигает Тень, возвращает (output, state)."""
    cmd = raw_cmd.strip().lower()
    parts = []

    # Прямой ввод кода сейфа (4 цифры в морге)
    if cmd.isdigit() and len(cmd) == 4 and state.current_room == "морг" and not state.puzzle_solved:
        out, _ = _capture(G.handle_puzzle_attempt, state, cmd)
        parts.append(out)

    # Блокируем run_puzzle от зависания на input() — заменяем описанием
    elif cmd in ("решить сейф", "решить головоломку", "открыть сейф",
                 "решить", "код", "сейф") and state.current_room == "морг":
        if state.puzzle_solved:
            parts.append("\033[90m  Сейф уже открыт.\033[0m\r\n")
        else:
            parts.append(
                "\033[96m\r\n  🔐 КОДОВЫЙ СЕЙФ\033[0m\r\n"
                "\033[37m  Четырёхзначный замок. На стене мелом — цифры.\r\n"
                "  Вспомни всё, что нашёл. Введи четырёхзначный код.\r\n"
                "\033[90m  (просто напечатай 4 цифры, например: 3721)\033[0m\r\n"
            )
    else:
        out, result = _capture(G.parse_command, cmd, state)
        parts.append(out)
        if isinstance(result, G.GameState):
            state = result

    # Тень движется и проверяется
    _capture(G.move_entity, state)
    enc_out, _ = _capture(G.check_entity_encounter, state)
    if enc_out.strip():
        parts.append(enc_out)

    # Вид комнаты после команды
    parts.append("\r\n" + _room_view(state))

    return "".join(parts), state

# ─── Стартовый экран ──────────────────────────────────────────

_TITLE = (
    "\033[2J\033[H"
    "\033[31m\033[1m\r\n"
    "  ██████╗  ██████╗  ██████╗ \r\n"
    "  ██╔══██╗██╔═══██╗██╔════╝ \r\n"
    "  ██████╔╝██║   ██║╚█████╗  \r\n"
    "  ██╔═══╝ ██║   ██║ ╚═══██╗ \r\n"
    "  ██║     ╚██████╔╝██████╔╝ \r\n"
    "  ╚═╝      ╚═════╝ ╚═════╝  \r\n"
    "\033[0m"
    "\033[91m\033[1m  ПОДВАЛ БЕЗУМИЯ\033[0m\r\n"
    "\033[90m  Текстовая хоррор-игра · Заброшенная психиатрическая больница\r\n\033[0m"
    "\033[90m══════════════════════════════════════════════════════════════════════\033[0m\r\n"
    "\033[37m  Новая игра начинается автоматически.\r\n"
    "  Тип \033[96mпомощь\033[37m для списка команд.\033[0m\r\n\r\n"
)

def _init_output(state) -> str:
    return _TITLE + _room_view(state)

# ─── HTML-страница ────────────────────────────────────────────

_HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Подвал Безумия</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.min.css">
<script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;background:#0a0a0a;font-family:'Courier New',monospace;overflow:hidden}
#app{display:flex;flex-direction:column;height:100vh;padding:10px 12px 10px;gap:8px}
#term-wrap{flex:1;min-height:0;border:1px solid #1e1e1e;border-radius:4px;overflow:hidden;background:#000}
#input-row{display:flex;align-items:center;gap:8px}
#prompt{color:#00d26a;font-size:15px;user-select:none;flex-shrink:0}
#cmd{flex:1;background:#111;border:1px solid #2a2a2a;color:#e0e0e0;
     font-family:'Courier New',monospace;font-size:14px;padding:7px 10px;
     outline:none;border-radius:3px;caret-color:#00d26a}
#cmd::placeholder{color:#3a3a3a}
#cmd:focus{border-color:#00d26a;box-shadow:0 0 0 1px #00d26a22}
#go{background:#0d1f0d;border:1px solid #2a2a2a;color:#00d26a;
    font-family:'Courier New',monospace;font-size:14px;padding:7px 14px;
    cursor:pointer;border-radius:3px;flex-shrink:0;transition:background 0.15s}
#go:hover{background:#142414;border-color:#00d26a}
#hints{color:#2e2e2e;font-size:11px;margin-top:3px;padding-left:2px}
#hints span{color:#3a3a3a}
</style>
</head>
<body>
<div id="app">
  <div id="term-wrap"><div id="terminal"></div></div>
  <div>
    <div id="input-row">
      <span id="prompt">&gt;</span>
      <input id="cmd" type="text" placeholder="введи команду..." autocomplete="off" spellcheck="false" autofocus>
      <button id="go">↵ Enter</button>
    </div>
    <div id="hints">
      <span>идти север/юг/запад/восток</span> &nbsp;·&nbsp;
      <span>осмотреть</span> &nbsp;·&nbsp;
      <span>взять [предмет]</span> &nbsp;·&nbsp;
      <span>использовать [предмет]</span> &nbsp;·&nbsp;
      <span>инвентарь</span> &nbsp;·&nbsp;
      <span>задания</span> &nbsp;·&nbsp;
      <span>помощь</span>
    </div>
  </div>
</div>
<script>
const SK = 'pdm_sid';
let sid = localStorage.getItem(SK) || '';
let term, fitAddon, busy = false;

function boot() {
  term = new Terminal({
    cols: 78, rows: 28,
    theme: {
      background:'#000000', foreground:'#cccccc',
      cursor:'#00d26a', cursorAccent:'#000',
      black:'#1e1e1e', red:'#cc3333', green:'#33cc66',
      yellow:'#ccaa33', blue:'#3377cc', magenta:'#cc33cc',
      cyan:'#33cccc', white:'#cccccc',
      brightBlack:'#555', brightRed:'#ff5555', brightGreen:'#55ff88',
      brightYellow:'#ffdd55', brightBlue:'#5599ff', brightMagenta:'#ff55ff',
      brightCyan:'#55ffff', brightWhite:'#ffffff'
    },
    fontFamily:"'Courier New', Courier, monospace",
    fontSize: 14, lineHeight: 1.28,
    convertEol: true, scrollback: 2000,
    cursorBlink: true,
  });
  fitAddon = new FitAddon.FitAddon();
  term.loadAddon(fitAddon);
  term.open(document.getElementById('terminal'));
  fitAddon.fit();
  new ResizeObserver(()=>fitAddon.fit()).observe(document.getElementById('term-wrap'));
}

async function post(path, body) {
  const r = await fetch(path, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  return r.json();
}

async function init() {
  term.write('\r\n  \x1b[90mЗагрузка...\x1b[0m');
  const d = await post('/init', {session: sid});
  sid = d.session;
  localStorage.setItem(SK, sid);
  term.write('\r\n' + d.output);
  document.getElementById('cmd').focus();
}

async function send() {
  if (busy) return;
  const inp = document.getElementById('cmd');
  const cmd = inp.value.trim();
  if (!cmd) return;
  busy = true;
  inp.value = '';
  term.write('\r\n\x1b[96m> ' + cmd + '\x1b[0m\r\n');
  try {
    const d = await post('/cmd', {session: sid, cmd});
    if (d.session) { sid = d.session; localStorage.setItem(SK, sid); }
    term.write(d.output);
    if (d.ended) {
      setTimeout(()=>{
        term.write('\r\n\x1b[90m[Начать заново — обнови страницу (F5)]\x1b[0m\r\n');
        localStorage.removeItem(SK);
        sid = '';
      }, 500);
    }
  } catch(e) {
    term.write('\r\n\x1b[31m  [ошибка связи]\x1b[0m\r\n');
  }
  busy = false;
  inp.focus();
}

document.getElementById('go').onclick = send;
document.getElementById('cmd').addEventListener('keydown', e => {
  if (e.key === 'Enter') send();
});

boot();
init();
</script>
</body>
</html>"""

# ─── HTTP-обработчик ──────────────────────────────────────────

class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass  # тишина в логах

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html):
        body = html.encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        n = int(self.headers.get('Content-Length', 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path in ('/', '/?'):
            self._send_html(_HTML)
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        data = self._read_json()

        if self.path == '/init':
            sid = data.get('session', '')
            state = _get_session(sid)
            if state is None:
                sid, state = _new_session()
            out = _init_output(state)
            self._send_json({'session': sid, 'output': out})

        elif self.path == '/cmd':
            sid  = data.get('session', '')
            cmd  = data.get('cmd', '').strip()
            state = _get_session(sid)
            if state is None:
                sid, state = _new_session()

            output, new_state = _process(state, cmd)
            sessions[sid] = new_state

            ended = new_state.won or new_state.dead
            if ended:
                sessions.pop(sid, None)

            self._send_json({'output': output, 'ended': ended})

        else:
            self.send_response(404); self.end_headers()

# ─── Точка входа ──────────────────────────────────────────────

if __name__ == '__main__':
    print(f"Подвал Безумия · веб-сервер · http://0.0.0.0:{PORT}", flush=True)
    server = HTTPServer(('0.0.0.0', PORT), _Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
