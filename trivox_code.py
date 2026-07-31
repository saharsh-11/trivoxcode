# =========================================================
# 👑 TRIVOXCODE v2.0.0 — CORE DEPENDENCIES & IMPORTS
# =========================================================
import os
import re
import sys
import json
import subprocess
import requests
from datetime import datetime

# --- Rich (Executive UI & Styling) ---
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt, Confirm

# --- Prompt Toolkit (Interactive CLI & HUD Layouts) ---
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout import Layout
from prompt_toolkit.application import Application

CONFIG_FILE = os.path.expanduser("~/.trivox_config.json")

def load_default_model():
    """Startup par saved default model load karta hai"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("default_model", "qwen3.5:9b")
        except Exception:
            pass
    return "qwen3.5:9b" 
def save_default_model(model_name: str):
    """User ke pasand ke default model ko permanent save karta hai"""
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    data["default_model"] = model_name
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


MODEL_NAME = load_default_model()

def confirm_risky_action(tool_name: str, target_details: str) -> bool:
    """
    Claude-Code Inspired Safety Guardrail:
    Risky tool chalane se pehle user se Allow/Reject confirmation leta hai.
    """
    # Tool ke hisab se warning color aur message set karo
    if "delete" in tool_name.lower() or "rm" in target_details.lower():
        action_type = "🚨 CRITICAL RISK: DELETION / REMOVAL"
        border_color = "bold red"
    elif "exec" in tool_name.lower() or "cmd" in tool_name.lower():
        action_type = "⚡ HIGH RISK: SHELL COMMAND EXECUTION"
        border_color = "bold yellow"
    else:
        action_type = "📝 FILE MODIFICATION / OVERWRITE"
        border_color = "bold cyan"

    warning_text = (
        f"[bold white]The autonomous agent is requesting permission to execute a potentially risky action:[/bold white]\n\n"
        f"  [bold {border_color}]• Action Type:[/] [white]{action_type}[/]\n"
        f"  [bold {border_color}]• Target / Cmd:[/] [bold bright_yellow]{target_details}[/]\n\n"
        f"[dim white]Do you want to allow TRIVOXCODE to proceed with this action?[/dim white]"
    )

    console.print(
        Panel(
            warning_text,
            title="[bold red]< USER PERMISSION REQUIRED / >[/bold red]",
            border_style=border_color,
            padding=(0, 1)
        )
    )

    # User se Allow (Y) ya Reject (N) pucho (Default: False/Reject for safety)
    try:
        user_approval = Confirm.ask("  [bold yellow]❯ Allow execution?[/bold yellow]", default=False)
        return user_approval
    except (KeyboardInterrupt, EOFError):
        return False

CONFIG_PATH = os.path.expanduser("~/.trivox_config.json")

def get_installed_ollama_models():
    """Ollama ke API se automatically local models fetch karta hai"""
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=3)
        if res.status_code == 200:
            models = [m["name"] for m in res.json().get("models", [])]
            return models if models else ["qwen2.5-coder:7b", "qwen3.5:9b"]
    except Exception:
        pass
    # Agar Ollama offline hai ya koi model nahi mila to fallback list
    return ["qwen2.5-coder:7b", "qwen3.5:9b", "llama3.1:8b", "mistral:7b"]

def select_model_interactive(models, theme_color="cyan"):
    """Terminal me sleek table dikhakar model select karwata hai"""
    table = Table(title="[bold]🤖 Detected Local Ollama Models[/bold]", border_style=theme_color)
    table.add_column("No.", style="bold white", width=6)
    table.add_column("Model Name", style=f"bold {theme_color}")
    table.add_column("Recommended Use", style="dim white")

    for idx, model in enumerate(models, 1):
        rec = "Best for Code & Fast CLI" if "coder" in model.lower() or "7b" in model.lower() else "Best for Deep Reasoning & Large Projects"
        table.add_row(f"[{idx}]", model, rec)

    console.print(table)
    
    while True:
        choice = input(f"\nSelect model number (1-{len(models)}) [Default: 1]: ").strip()
        if not choice:
            return models[0]
        if choice.isdigit() and 1 <= int(choice) <= len(models):
            return models[int(choice) - 1]
        console.print("[red]✖ Invalid selection, try again.[/red]")

       # 4 Premium Themes Blueprint
THEMES = {
    "1": {"name": "TrivoX Cyber Cyan (Claude Code Vibe)", "color": "cyan", "accent": "white", "bg_style": "bg:#1e293b #0ea5e9"},
    "2": {"name": "Neon Emerald (Terminal Hacker)", "color": "green", "accent": "bright_white", "bg_style": "bg:#064e3b #10b981"},
    "3": {"name": "Royal Indigo (Aider / SaaS Vibe)", "color": "magenta", "accent": "white", "bg_style": "bg:#312e81 #818cf8"},
    "4": {"name": "Sunset Gold (Retro Elite)", "color": "yellow", "accent": "white", "bg_style": "bg:#451a03 #f59e0b"}
}

def first_time_setup():
    """First-time installation par Theme aur Model select karwakar save karta hai"""
    console.print("\n[bold cyan]✨ Welcome to TrivoX Code — First-Time Environment Setup[/bold cyan]\n")
    
    # Theme Selection Table
    table = Table(title="[bold]🎨 Select Your CLI Theme Palette[/bold]", border_style="dim")
    table.add_column("No.", style="bold white", width=6)
    table.add_column("Theme Name", style="bold")
    table.add_column("Accent Preview", style="bold")

    table.add_row("[1]", "TrivoX Cyber Cyan (Default)", "[cyan]■■■■■■■■ cyan & slate[/cyan]")
    table.add_row("[2]", "Neon Emerald (Hacker)", "[green]■■■■■■■■ green & dark[/green]")
    table.add_row("[3]", "Royal Indigo (Modern)", "[magenta]■■■■■■■■ indigo & violet[/magenta]")
    table.add_row("[4]", "Sunset Gold (Retro)", "[yellow]■■■■■■■■ gold & amber[/yellow]")
    console.print(table)

    theme_idx = input("\nSelect theme number (1-4) [Default: 1]: ").strip() or "1"
    selected_theme = THEMES.get(theme_idx, THEMES["1"])

    # Model Selection
    models = get_installed_ollama_models()
    selected_model = select_model_interactive(models, selected_theme["color"])

    config_data = {
        "model": selected_model,
        "theme_color": selected_theme["color"],
        "bg_style": selected_theme["bg_style"],
        "setup_complete": True
    }

    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=2)

    console.print(f"\n[bold green]✔ Configuration saved to {CONFIG_PATH}![/bold green]\n")
    return config_data

# =========================================================
# 🎮 INTERACTIVE LIVE THEME SELECTOR (UP/DOWN ARROW PREVIEW)
# =========================================================
def select_theme_interactive():
    themes = [
        {"name": "Sunset Gold (Executive Default)", "code": "1", "ansi": "ansiyellow"},
        {"name": "Cyber Blue (Futuristic Tech)", "code": "2", "ansi": "ansicyan"},
        {"name": "Neon Emerald (Matrix Coder)", "code": "3", "ansi": "ansigreen"},
        {"name": "Royal Indigo (Premium Synth)", "code": "4", "ansi": "ansimagenta"},
    ]
    selected_idx = [0]  # Closure ke liye list
    kb = KeyBindings()

    @kb.add("up")
    def _up(event):
        selected_idx[0] = (selected_idx[0] - 1) % len(themes)

    @kb.add("down")
    def _down(event):
        selected_idx[0] = (selected_idx[0] + 1) % len(themes)

    @kb.add("enter")
    def _enter(event):
        event.app.exit(result=themes[selected_idx[0]]["code"])

    def get_content():
        current = themes[selected_idx[0]]
        lines = [
            "  <b>[UP / DOWN ARROW] दबाकर थीम बदलें और लाइव प्रिव्यू देखें, [ENTER] दबाकर सेलेक्ट करें:</b>\n\n"
        ]
        
        for i, theme in enumerate(themes):
            pointer = " ❯ " if i == selected_idx[0] else "   "
            style_start = f"<{theme['ansi']}><b>" if i == selected_idx[0] else "<ansigray>"
            style_end = f"</b></{theme['ansi']}>" if i == selected_idx[0] else "</ansigray>"
            lines.append(f"{pointer}{style_start}{i+1}. {theme['name']}{style_end}\n")
        
        # 🎨 Complete TRIVOXCODE Executive HUD (Mathematically Aligned & Spell-Checked)
        c = current["ansi"]
        lines.append("\n  <b>┌─── LIVE THEME PREVIEW : TRIVOXCODE HUD ─────────────────────────────┐</b>\n")
        lines.append(f"  │  <{c}><b>████████╗██████╗ ██╗██╗   ██╗ ██████╗ ██╗  ██╗</b></{c}>   <b>[ TRIVOXCODE ]</b>    │\n")
        lines.append(f"  │  <{c}><b>╚══██╔══╝██╔══██╗██║██║   ██║██╔═══██╗╚██╗██╔╝</b></{c}>   Autonomous Code   │\n")
        lines.append(f"  │  <{c}><b>   ██║   ██████╔╝██║╚██╗ ██╔╝██║   ██║ ╚███╔╝ </b></{c}>    Workbench v2.0    │\n")
        lines.append(f"  │  <{c}><b>   ██║   ██╔══██╗██║ ╚████╔╝ ██║   ██║ ██╔██╗ </b></{c}>    TrivoX Tech AI    │\n")
        lines.append(f"  │  <{c}><b>   ██║   ██║  ██║██║  ╚██╔╝  ╚██████╔╝██╔╝ ██╗</b></{c}>   Zero Infinite     │\n")
        lines.append("  └─────────────────────────────────────────────────────────────────────┘\n")
        lines.append(f"  Selected Mode: <{c}><b>{current['name']}</b></{c}>\n")
        return HTML("".join(lines))

    app = Application(
        layout=Layout(Window(FormattedTextControl(get_content))),
        key_bindings=kb,
        full_screen=False
    )
    return app.run()

# =========================================================
# 🔍 OLLAMA ENGINE & MODEL VERIFICATION HELPER
# =========================================================
def check_ollama_models():
    """Ollama running hai ya nahi check karta hai aur installed models return karta hai"""
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=3)
        if res.status_code == 200:
            models = [m["name"] for m in res.json().get("models", [])]
            return True, models
    except Exception:
        pass
    return False, []

# =========================================================
# 👑 ADVANCED FIRST TIME SETUP WIZARD v2.1
# =========================================================
def run_setup_wizard():
    CONFIG_PATH = os.path.expanduser("~/.trivox_config.json")
    if os.path.exists(CONFIG_PATH):
        return

    console.print(Panel.fit(
        "[bold yellow]👑 TRIVOX TECHNOLOGIES — ADVANCED FIRST TIME SETUP[/bold yellow]\n"
        "[white]System health check, AI Model Verification & Interactive Theme Customizer[/white]",
        border_style="yellow"
    ))

    # 1. 🔍 Ollama Health Check
    console.print("\n[bold cyan]Step 1: Checking Ollama AI Engine...[/bold cyan]")
    is_running, installed_models = check_ollama_models()

    if not is_running:
        console.print("[bold red]✖ WARNING: Ollama Engine is NOT running or NOT installed![/bold red]")
        console.print("[yellow]👉 To download Ollama: Visit [bold white]https://ollama.com/download[/bold white][/yellow]")
        console.print("[yellow]👉 If already installed, open a terminal and run: [bold white]ollama serve[/bold white][/yellow]\n")
    else:
        console.print(f"[bold green]✔ Ollama Engine Active![/bold green] Found [bold white]{len(installed_models)}[/bold white] models in your local library.\n")

    # 2. ⭐ Model Selection & Verification
    console.print("[bold cyan]Step 2: Select Default Local LLM Model[/bold cyan]")
    console.print("[bold yellow]⭐ HIGHLY RECOMMENDED (Default):[/bold yellow] [white]qwen3.5:9b[/white] [dim](Best reasoning + coding balance)[/dim]")
    console.print("[bold green]🚀 RECOMMENDED ALTERNATIVE:[/bold green]     [white]qwen2.5-coder:7b[/white] [dim](Fast & specialized for code)[/dim]\n")

    while True:
        model_choice = input("❯ Enter model name (Default: qwen3.5:9b): ").strip()
        if not model_choice:
            model_choice = "qwen3.5:9b"

        # Check if model is downloaded in Ollama
        if is_running and model_choice not in installed_models:
            console.print(f"\n[bold red]⚠️ WARNING: '{model_choice}' is NOT installed in your Ollama library![/bold red]")
            console.print(f"[bold yellow]👉 To download it, open a terminal and run:[/bold yellow] [bold white]ollama pull {model_choice}[/bold white]\n")
            confirm = input(f"❯ Do you still want to set '{model_choice}' as default? [y/n] (n): ").strip().lower()
            if confirm == "y":
                break
            else:
                console.print("[dim]Let's select a valid or recommended model name...[/dim]\n")
                continue
        else:
            if is_running:
                console.print(f"[bold green]✔ Verified:[/bold green] [white]'{model_choice}'[/white] is installed and ready to code!\n")
            break

    # 3. 🎨 Interactive Theme Selection with Live Preview
    console.print("[bold cyan]Step 3: Select Executive UI Theme Color[/bold cyan]")
    theme_choice = select_theme_interactive()

    # 4. Save Config
    config_data = {
        "default_model": model_choice,
        "theme_color": theme_choice
    }
    
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
        console.print(f"\n[bold green]✔ Setup Complete![/bold green] Preferences saved to [white]{CONFIG_PATH}[/white]\n")
    except Exception as e:
        console.print(f"[bold red]✖ Failed to save config:[/bold red] {e}")
# ==========================================
# 🎨 1. INTERACTIVE SLASH DROPDOWN MENU (AUTO-POPUP FIX)
# ==========================================
slash_completer = WordCompleter(
    [
        '/model qwen3.5:9b',
        '/model qwen2.5-coder:7b',
        '/default',
        '/config',
        '/clear',
        '/help',
        '/exit'
    ], 
    ignore_case=True, 
    sentence=True,
    pattern=re.compile(r'[/\w-]+')  
)



dropdown_style = Style.from_dict({
    'completion-menu.completion': 'bg:#1e293b #0ea5e9',
    'completion-menu.completion.current': 'bg:#0ea5e9 #ffffff bold',
})

# ==========================================
# ⌨️ 2. KEYBINDINGS: ESC TO DISMISS DROPDOWN
# ==========================================
kb = KeyBindings()

@kb.add('escape')
def _(event):
    """ESC dabate hi agar dropdown khula hai to wo turant cancel ho jayega"""
    buffer = event.app.current_buffer
    if buffer.complete_state:
        buffer.cancel_completion()

# ==========================================
# 🎨 FOOLPROOF COLORFUL PROMPT (Tuple Format)
# ==========================================

def chat_with_agent():
    global MODEL_NAME


    styled_prompt = [
        ('ansiyellow bold', 'TrivoX '),
        ('ansiwhite bold', 'Code '),
        ('ansiyellow bold', '❯ ')
    ]
    session = PromptSession(
        completer=slash_completer,
        style=dropdown_style,
        complete_while_typing=True,
        key_bindings=kb
    )
    
    while True:
        try:
           
            user_input = session.prompt(styled_prompt).strip()
            
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
console = Console()

YELLOW_THEME = Style.from_dict({
    'prompt': 'ansiyellow bold',
    'input': 'ansiwhite',
})

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.5:9b"
MEMORY_FILE = ".trivox_memory.json"

# ==========================================
# 🧠 1. MEMORY MANAGEMENT MODULE
# ==========================================
def load_memory() -> dict:
    """Loads stored project context & rules."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_to_memory(key: str, value: str):
    """Saves long-term facts to local JSON."""
    mem = load_memory()
    mem[key] = value
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2)
        console.print(f"[bold cyan]🧠 [MEMORY SAVED]:[/bold cyan] [{key}] -> {value}")
    except Exception as e:
        console.print(f"[bold red]✖ Memory Error:[/bold red] {e}")

def get_memory_context_string() -> str:
    mem = load_memory()
    if not mem:
        return "No long-term memory stored yet."
    return "\n".join([f"- {k}: {v}" for k, v in mem.items()])

# ==========================================
# ⚡ UNIVERSAL CODER PROMPT (FOR 7B & 9B)
# ==========================================
def get_coder_system_prompt() -> str:
    memory_context = get_memory_context_string()
    # 👇 Yeh har PC ka real system date aur time dynamically uthayega
    current_time_str = datetime.now().strftime("%A, %B %d, %Y (%I:%M %p)")
    return f"""You are TrivoX Code (CODER AGENT), an autonomous AI coding agent by TrivoX Technologies.
    CURRENT SYSTEM REAL-TIME CLOCK: {current_time_str}

    CRITICAL RULES FOR INTRODUCTIONS & CHIT-CHAT (ANTI-DEMO GUARDRAIL):
1. NO XML TOOL DEMOS: If the user asks general questions like "who are you", "what can you do", "help", or asks to explain your features, NEVER emit any XML tags (<write_file>, <delete_file>, <execute_command>, <web_search>, etc.) in your response.
2. PLAIN TEXT ONLY: Explain your capabilities using plain English Markdown bullet points ONLY. Do not execute or simulate tool calls unless the user explicitly commands you to perform a real project task.

IMPORTANT: Always use the above CURRENT SYSTEM REAL-TIME CLOCK as the absolute ground truth for today's date and year. Never assume older years like 2024 or 2025.
=== LONG-TERM PROJECT MEMORY ===
{memory_context}
================================

=== AVAILABLE XML SKILLS (USE ONLY THESE) ===
1. Write a file (ALWAYS put code inside tags):
   <write_file path="folder/file.py">full code here</write_file>

2. Read an existing file:
   <read_file path="file.py" />

3. List files in a folder (Never use ls or dir commands, use this instead):
   <list_dir path="." />

4. Delete a temporary or broken file:
   <delete_file path="temp.py" />

5. Search the web for docs or solutions:
   <web_search query="FastAPI authentication syntax" />

6. Run terminal/system commands (e.g. testing, pip install):
   <run_command>pytest</run_command>

7. Save important project facts to memory:
   <save_memory key="tech_stack">FastAPI + React</save_memory>

8. Finish the task:
   <done>Task completion summary</done>

=== CRITICAL RULES ===
- Execute multiple required tags in a SINGLE response (Batching).
- Use <list_dir> instead of shell listing commands.
- Never write placeholder code or comments like '# rest of code'.
"""
def get_manager_system_prompt() -> str:
    # 👇 Yeh har PC ka real system date aur time dynamically uthayega
    current_time_str = datetime.now().strftime("%A, %B %d, %Y (%I:%M %p)")
    
    return f"""You are the TrivoX Manager (ARCHITECT AGENT) at TrivoX Technologies.
CURRENT SYSTEM REAL-TIME CLOCK: {current_time_str}

# Manager Agent के System Prompt में ये लाइनें जोड़ो:

CRITICAL RULES FOR CONTEXT AWARENESS:
1. READ PREVIOUS MESSAGES: Always analyze the immediate previous message sent by the "Coder Agent" in the chat history before answering.
2. PRONOUN RESOLUTION: If the user says "run step 1", "do this", "execute the next steps", or uses pointers like "this/that", DO NOT ask for clarification. Instead, look at the Coder Agent's last message, figure out what those steps are, and create a roadmap to execute them.

IMPORTANT: Always use the above CURRENT SYSTEM REAL-TIME CLOCK as the absolute ground truth for today's date and year. Never assume older years like 2024 or 2025.
Your ONLY job is to analyze the user's high-level request and break it down into 2-3 clear, simple plain-English steps for the Coder Agent.

STRICT RULE: NEVER write XML tags (like <write_file>, <run_command>, <save_memory>) or raw code in your roadmap. Write ONLY plain English instructions so the Coder Agent can format the tools correctly itself.
"""

# ==========================================
# 👑 SINGLE-BOX BANNER FOR TRIVOXCODE
# ==========================================
def show_banner(theme_color="yellow", model_name=None):
    """Pristine Single-Box Executive Banner for TRIVOXCODE"""
    
   
    if model_name is None:
        model_name = MODEL_NAME
    
    banner_art = f"""[{theme_color}]
 ████████╗██████╗ ██╗██╗   ██╗ ██████╗ ██╗  ██╗ ██████╗ ██████╗ ██████╗ ███████╗
 ╚══██╔══╝██╔══██╗██║██║   ██║██╔═══██║╚██╗██╔╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
    ██║   ██████╔╝██║██║   ██║██║   ██║ ╚███╔╝ ██║     ██║   ██║██║  ██║█████╗  
    ██║   ██╔══██╗██║╚██╗ ██╔╝██║   ██║ ██╔██╗ ██║     ██║   ██║██║  ██║██╔══╝  
    ██║   ██║  ██║██║ ╚████╔╝ ╚██████╔╝██╔╝ ██╗╚██████╗╚██████╔╝██████╔╝███████╗
[/]"""

    banner_content = f"""{banner_art}
[bold white]  AUTONOMOUS AGENTIC CODE WORKBENCH[/bold white]  [{theme_color}] | [/]  [bold blue]TrivoX Technologies v2.0.0[/bold blue]
[bold bright_yellow]  ⚡ ENGINEERED FOR SUB-10B & LOW-BILLION LOCAL MODELS[/bold bright_yellow]  [{theme_color}] | [/]  [bold green]ZERO HALLUCINATION XML[/bold green]

  [{theme_color}]❯[/] [dim]Active Engine:[/] [bold {theme_color}]{model_name}[/]    [{theme_color}] | [/]    [dim]Backend:[/] [bold white]Ollama[/]    [{theme_color}] | [/]    [dim]Memory:[/] [bold green]Active[/]"""
    
    console.print(
        Panel(
            banner_content,
            title=f"[bold {theme_color}]< TRIVOXCODE / >[/bold {theme_color}]",
            border_style=f"bold {theme_color}",
            padding=(0, 1),
            expand=False
        )
    )
    
def execute_tools(response_text: str) -> list:
    results = []

    # =========================================================
    # 1. WRITE FILES (RISKY ACTION - PERMISSION REQUIRED)
    # =========================================================
    write_matches = re.findall(r'<write_file\s+path=["\'](.*?)["\']>(.*?)</write_file>', response_text, re.DOTALL | re.IGNORECASE)
    for path, content in write_matches:
        path = path.strip()
        content = content.strip()
        
        # 🛡️ GUARDRAIL: User se pehle pucho!
        if not confirm_risky_action("WRITE_FILE", f"Overwrite/Create: {path} ({len(content.splitlines())} lines)"):
            console.print(f"[bold red]✖ Permission Denied:[/bold red] Aborted writing '{path}'.")
            results.append(f"Error: User REJECTED permission to write file '{path}'.")
            continue

        console.print(f"[bold yellow]💾 [WRITE FILE]:[/bold yellow] [white]{path}[/white]")
        try:
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            results.append(f"File '{path}' written successfully.")
            console.print(f"[bold green]✔ Saved:[/bold green] {path} ({len(content.splitlines())} lines)")
        except Exception as e:
            results.append(f"Error writing file '{path}': {str(e)}")
            console.print(f"[bold red]✖ Save Failed:[/bold red] {str(e)}")

    # =========================================================
    # 2. READ FILE SKILL (SAFE ACTION - NO PERMISSION NEEDED)
    # =========================================================
    read_matches = re.findall(r'<read_file\s+path=["\'](.*?)["\']\s*/?>', response_text, re.IGNORECASE)
    for path in read_matches:
        path = path.strip()
        console.print(f"[bold yellow]📖 [READ FILE]:[/bold yellow] [white]{path}[/white]")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            results.append(f"Content of '{path}':\n{data}")
            console.print(f"[bold green]✔ Read Complete:[/bold green] {path} ({len(data.splitlines())} lines)")
        except Exception as e:
            results.append(f"Error reading file '{path}': {str(e)}")
            console.print(f"[bold red]✖ Read Failed:[/bold red] {str(e)}")

    # =========================================================
    # 3. LIST DIR SKILL (SAFE ACTION - NO PERMISSION NEEDED)
    # =========================================================
    list_matches = re.findall(r'<list_dir\s+path=["\'](.*?)["\']\s*/?>', response_text, re.IGNORECASE)
    for path in list_matches:
        path = path.strip() or "."
        console.print(f"[bold yellow]📂 [LIST DIR]:[/bold yellow] [white]{path}[/white]")
        try:
            items = os.listdir(path)
            clean_items = [i for i in items if i not in ['.git', '__pycache__', '.venv', 'node_modules']]
            results.append(f"Directory '{path}' contains:\n" + "\n".join(f" - {i}" for i in clean_items))
            console.print(f"[bold green]✔ Listed:[/bold green] {len(clean_items)} items in '{path}'")
        except Exception as e:
            results.append(f"Error listing directory '{path}': {str(e)}")
            console.print(f"[bold red]✖ List Failed:[/bold red] {str(e)}")

    # =========================================================
    # 4. DELETE FILE SKILL (CRITICAL RISKY ACTION - PERMISSION REQUIRED)
    # =========================================================
    del_matches = re.findall(r'<delete_file\s+path=["\'](.*?)["\']\s*/?>', response_text, re.IGNORECASE)
    for path in del_matches:
        path = path.strip()
        
        # 🛡️ GUARDRAIL: User se pehle pucho!
        if not confirm_risky_action("DELETE_FILE", f"Permanent Deletion: {path}"):
            console.print(f"[bold red]✖ Permission Denied:[/bold red] Aborted deleting '{path}'.")
            results.append(f"Error: User REJECTED permission to delete file '{path}'.")
            continue

        console.print(f"[bold yellow]🗑️ [DELETE FILE]:[/bold yellow] [white]{path}[/white]")
        try:
            if os.path.exists(path):
                os.remove(path)
                results.append(f"File '{path}' deleted successfully.")
                console.print(f"[bold green]✔ Deleted:[/bold green] {path}")
            else:
                results.append(f"File '{path}' does not exist.")
                console.print(f"[bold red]✖ Not Found:[/bold red] {path}")
        except Exception as e:
            results.append(f"Error deleting file '{path}': {str(e)}")
            console.print(f"[bold red]✖ Delete Failed:[/bold red] {str(e)}")

    # =========================================================
    # 5. WEB SEARCH SKILL (DDGS Bulletproof Search & Anti-Loop)
    # =========================================================
    search_matches = re.findall(r'<web_search\s+query=["\'](.*?)["\']\s*/?>', response_text, re.IGNORECASE)
    for query in search_matches:
        query = query.strip()
        console.print(f"[bold yellow]🌐 [WEB SEARCH]:[/bold yellow] [white]{query}[/white]")
        
        try:
            # 🔇 Kisi bhi tarah ki Rename ya Deprecation Warning ko poora mute karne ke liye
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                warnings.filterwarnings("ignore", category=UserWarning)
                warnings.simplefilter("ignore")
                try:
                    from ddgs import DDGS
                except ImportError:
                    from duckduckgo_search import DDGS
                   
            with DDGS() as ddgs:
                # Pehle .text() try karo, agar empty aaye to smart search syntax use karo
                search_results = list(ddgs.text(query, max_results=5))
                if not search_results and "news" in query.lower():
                    try:
                        search_results = list(ddgs.news(query, max_results=5))
                    except Exception:
                        pass
            
            if search_results:
                summary = "\n".join([f"• {r.get('title', '')}: {r.get('body', '')} ({r.get('href', '')})" for r in search_results])
                status_msg = f"Found {len(search_results)} web results"
            else:
                summary = "No direct live links returned by DuckDuckGo for this query. Use your existing knowledge to summarize."
                status_msg = "Found 0 web results (Query too restrictive)"

            # 👇 MAGIC ANTI-LOOP GUARDRAIL
            results.append(
                f"Search results for '{query}':\n{summary}\n\n"
                f"⚠️ [SYSTEM DIRECTIVE]: You have enough information now. DO NOT call <web_search> again. "
                f"Immediately summarize these findings clearly to the user in plain English, "
                f"and close your response with <done>Task Completed</done>."
            )
            console.print(f"[bold green]✔ Search Complete:[/bold green] {status_msg}")
        except Exception as e:
            results.append(f"Web search failed for '{query}': {str(e)}")
            console.print(f"[bold red]✖ Search Failed:[/bold red] {str(e)}")
    # =========================================================
    # 6. SAVE MEMORY
    # =========================================================
    mem_matches = re.findall(r'<save_memory\s+key=["\'](.*?)["\']>(.*?)</save_memory>', response_text, re.DOTALL | re.IGNORECASE)
    for key, val in mem_matches:
        save_to_memory(key.strip(), val.strip())
        results.append(f"Memory saved: [{key.strip()}] = {val.strip()}")

    # =========================================================
    # 7. RUN COMMANDS (HIGH RISKY ACTION - PERMISSION REQUIRED)
    # =========================================================
    cmd_matches = re.findall(r"<run_command>(.*?)</run_command>", response_text, re.DOTALL | re.IGNORECASE)
    for cmd in cmd_matches:
        cmd = cmd.strip()
        
        # 🛡️ GUARDRAIL: Shell command chalane se pehle permission!
        if not confirm_risky_action("EXEC_CMD", f"Shell Command: {cmd}"):
            console.print(f"[bold red]✖ Permission Denied:[/bold red] Aborted command '{cmd}'.")
            results.append(f"Error: User REJECTED permission to execute command '{cmd}'.")
            continue

        console.print(f"[bold yellow]⚡ [EXEC COMMAND]:[/bold yellow] [white]{cmd}[/white]")
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            results.append(f"Command '{cmd}' Output:\n{output}")
            console.print(Panel(output.strip()[:500] if output else "Success (No output)", border_style="dim yellow", title="Command Result"))
        except subprocess.CalledProcessError as e:
            results.append(f"Command '{cmd}' Failed:\n{e.output}")
            console.print(f"[bold red]✖ Error:[/bold red] {e.output}")

    return results

# ==========================================
# 🚀 API CALL WITH ANTI-HALLUCINATION CONFIG
# ==========================================
def call_ollama(messages: list) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.15,   # Keeps 9B strictly disciplined & stops hallucination
                "num_ctx": 8192,       # Allows large 150+ line files without breaking
                "top_p": 0.9           # Focuses on high-accuracy tokens only
            }
        },
        timeout=180
    )
    return response.json().get("message", {}).get("content", "")

def chat_with_agent():
    global MODEL_NAME
    
    styled_prompt = HTML('<ansiyellow><b>TRIVOX CODE ❯ </b></ansiyellow>')

    session = PromptSession(
        completer=slash_completer,
        style=dropdown_style,
        complete_while_typing=True,
        key_bindings=kb
    )
    
    while True:
        try:
           
            user_input = session.prompt(styled_prompt).strip()
            
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        # ==========================================
        # ⚙️ STRICT SLASH COMMAND HANDLER (NO LOOP BUG)
        # ==========================================
        if user_input.startswith("/"):
            parts = user_input.split()
            cmd = parts[0].lower()

            
            if cmd == "/default":
                if len(parts) > 1:
                    new_default = parts[1]
                    save_default_model(new_default)
                    MODEL_NAME = new_default
                    console.print(f"[bold green]✔ Default Startup Model permanently set to:[/bold green] [cyan]{new_default}[/cyan]")
                else:
                    console.print("[bold red]✖ Please specify a model name![/bold red] (e.g. /default qwen3.5:9b)")
                continue

            elif cmd == "/model":
                if len(parts) > 1:
                    MODEL_NAME = parts[1]
                    console.print(f"[bold green]✔ Model switched to:[/bold green] [cyan]{MODEL_NAME}[/cyan]")
                else:
                    console.print("[bold red]✖ Please specify a model name![/bold red] (e.g. /model qwen3.5:9b)")
                continue  
            elif cmd == "/config":
                console.print(Panel(
                    f"• [bold]Active Model:[/bold] [cyan]{MODEL_NAME}[/cyan]\n"
                    f"• [bold]Ollama URL:[/bold] {OLLAMA_URL}\n"
                    f"• [bold]Memory File:[/bold] .trivox_memory.json\n"
                    f"• [bold]Context Window:[/bold] 8192 tokens\n"
                    f"• [bold]Temperature:[/bold] 0.15 (Strict Developer Mode)",
                    title="⚙️ TrivoX Code CLI Configuration",
                    border_style="cyan"
                ))
                continue

            elif cmd == "/clear":
                if os.path.exists(".trivox_memory.json"):
                    os.remove(".trivox_memory.json")
                console.print("[bold yellow]🧹 Project memory cleared successfully![/bold yellow]")
                continue

            elif cmd in ["/help", "/?"]:
                console.print("[bold cyan]Available Slash Commands:[/bold cyan]\n"
                              "  /model <name>  -> Switch LLM model instantly\n"
                              "  /config        -> Show active settings\n"
                              "  /clear         -> Erase project long-term memory\n"
                              "  /exit          -> Exit CLI")
                continue

            elif cmd == "/exit":
                break

            else:
                console.print(f"[bold red]✖ Unknown command:[/bold red] {cmd}. Type [cyan]/help[/cyan] to see options.")
                continue

        # ==========================================
        # 🧠 NORMAL AI PROMPT EXECUTION
        # ==========================================
        try:
            # --- STEP 1: MANAGER AGENT (PLANNING) ---
            with console.status("[bold cyan]🧠 Manager Agent is designing the implementation roadmap...[/bold cyan]", spinner="dots"):
                manager_messages = [
                    {"role": "system", "content": get_manager_system_prompt()},
                    {"role": "user", "content": user_input}
                ]
                roadmap = call_ollama(manager_messages)
            
            console.print(Panel(Markdown(roadmap.strip()), border_style="cyan", title="[bold cyan]🧠 Manager Agent Roadmap[/bold cyan]"))

            # --- STEP 2: CODER AGENT (EXECUTION LOOP) ---
            coder_messages = [
                {"role": "system", "content": get_coder_system_prompt()},
                {"role": "user", "content": f"Here is the plan from Manager Agent:\n{roadmap}\n\nUser Request: {user_input}\nExecute this plan step-by-step using XML tools."}
            ]

            step_count = 0
            while step_count < 10:
                step_count += 1
                
                with console.status(f"[bold yellow]⚡ Coder Agent is executing (Step #{step_count})...[/bold yellow]", spinner="dots"):
                    assistant_message = call_ollama(coder_messages)
                
                coder_messages.append({"role": "assistant", "content": assistant_message})

                # 🧹 Clean all XML tool tags for a pristine terminal UI
                clean_text = re.sub(r'<write_file.*?>.*?</write_file>', '[File Written...]', assistant_message, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<run_command>.*?</run_command>', '[Command Executed...]', clean_text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<save_memory.*?>.*?</save_memory>', '[Memory Updated...]', clean_text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r'<read_file.*?>', '[File Read...]', clean_text, flags=re.IGNORECASE)
                clean_text = re.sub(r'<list_dir.*?>', '[Directory Listed...]', clean_text, flags=re.IGNORECASE)
                clean_text = re.sub(r'<delete_file.*?>', '[File Deleted...]', clean_text, flags=re.IGNORECASE)
                clean_text = re.sub(r'<web_search.*?>', '[Web Search Executed...]', clean_text, flags=re.IGNORECASE)

                console.print(Panel(Markdown(clean_text.strip()), border_style="yellow", title=f"[bold yellow]⚡ Coder Agent Step #{step_count}[/bold yellow]"))

                # 🛠️ Execute all tools
                tool_outputs = execute_tools(assistant_message)

                if "<done>" in assistant_message or not tool_outputs:
                    done_match = re.search(r"<done>(.*?)</done>", assistant_message, re.DOTALL | re.IGNORECASE)
                    if done_match:
                        console.print(f"\n[bold green]🏆 [TASK COMPLETED]:[/bold green] {done_match.group(1).strip()}")
                    break

                # 🔄 Feedback loop to continue execution
                feedback_content = "Tool Execution Results:\n" + "\n---\n".join(tool_outputs)
                coder_messages.append({"role": "user", "content": feedback_content})

        except KeyboardInterrupt:
            console.print("\n[bold red]✖ Operation Cancelled by User.[/bold red]")
            continue
        except Exception as e:
            console.print(f"\n[bold red]✖ System Error:[/bold red] {str(e)}")
            continue

# ==========================================
# 🚀 PROGRAM ENTRY POINT 
# ==========================================
def load_default_model():
    """Reads default model from ~/.trivox_config.json"""
    config_path = os.path.expanduser("~/.trivox_config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = json.load(f)
                return data.get("default_model", "qwen3.5:9b")
    except Exception:
        pass
    return "qwen3.5:9b"

def get_theme_color():
    """Reads saved theme choice (1-4) and maps to rich color name"""
    config_path = os.path.expanduser("~/.trivox_config.json")
    theme_map = {
        "1": "yellow",
        "2": "cyan",
        "3": "green",
        "4": "magenta"
    }
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = json.load(f)
                code = str(data.get("theme_color", "1"))
                return theme_map.get(code, "yellow")
    except Exception:
        pass
    return "yellow"

# ==========================================
# 🚀 PROGRAM ENTRY POINT
# ==========================================
def main():
    """CLI Entry point for TrivoX Code"""
    # 1. Pehle first-time setup wizard check karo
    run_setup_wizard()
    
    # 2. Config se saved model aur theme uthao
    global MODEL_NAME
    MODEL_NAME = load_default_model()
    ACTIVE_THEME = get_theme_color()

    # 3. Selected theme ke sath banner show karo
    try:
        show_banner(theme_color=ACTIVE_THEME, model_name=MODEL_NAME)
    except TypeError:
        # Agar show_banner bina arguments wala defined hai to safely fallback karo
        show_banner()
    
    # 4. Asli Chat loop chalu karo
    chat_with_agent()

if __name__ == "__main__":
    main()