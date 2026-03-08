"""
app.py — OmniMarkdown local main application
Usage:  python app.py
Install: pip install gradio openai httpx
"""

import os
import gradio as gr

from skills_loader import load_skills, match_skill
from llm_client import LLMClient

# ── Path config ──────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR  = os.path.join(BASE_DIR, "skills")
NOTE_PATH   = os.path.join(BASE_DIR, "user_files", "notebook.md")
CONFIG_PATH = os.path.join(BASE_DIR, "llm_config.json")

# ── Load skills & LLM on startup ─────────────────────────
print("\n========== OmniMarkdown Starting ==========")
SKILLS = load_skills(SKILLS_DIR)
print(f"{len(SKILLS)} skill(s) loaded\n")

try:
    LLM = LLMClient(CONFIG_PATH)
    print(f"[LLM] Model: {LLM.model_name}  Ready ✅\n")
except Exception as e:
    LLM = None
    print(f"[LLM] ⚠️  Failed to load: {e}\nPlease check llm_config.json\n")

# ── Note read / write ────────────────────────────────────
def read_note() -> str:
    try:
        with open(NOTE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "# My Notebook\n\n(Empty — start adding notes!)"

def write_note(content: str):
    os.makedirs(os.path.dirname(NOTE_PATH), exist_ok=True)
    with open(NOTE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

# ── Skill button click: fill prefix into input ───────────
def on_skill_click(prefix: str, current_input: str) -> str:
    clean_prefix = prefix.strip("`").strip()
    if current_input.strip().startswith(clean_prefix):
        return current_input
    return clean_prefix + " "

# ── Core: handle user message ────────────────────────────
def on_send(user_input: str, history: list, note_content: str):
    user_input = user_input.strip()
    if not user_input:
        return history, note_content, "", "⚠️ Please enter a message"

    if LLM is None:
        err = "❌ LLM not initialized. Please check llm_config.json and restart."
        history = history + [[user_input, err]]
        return history, note_content, "", "LLM not ready"

    skill, instruction = match_skill(user_input, SKILLS)

    if skill is None:
        reply = "❓ No matching skill found. Use ? to query or ! add / delete / modify to edit notes."
        history = history + [[user_input, reply]]
        return history, note_content, "", "No matching skill"

    try:
        sys_prompt  = skill.system_prompt
        user_prompt = skill.build_user_prompt(note_content, instruction)
        result      = LLM.chat(sys_prompt, user_prompt)
    except Exception as e:
        reply = f"❌ LLM call failed: {e}"
        history = history + [[user_input, reply]]
        return history, note_content, "", "LLM call failed"

    is_edit = skill.skill_id in ("add", "delete", "modify")

    if is_edit:
        write_note(result)
        new_note = result
        reply    = f"✅ [{skill.icon} {skill.label}] Done! Note updated — check the right panel."
        status   = f"{skill.icon} Note saved"
    else:
        new_note = note_content
        reply    = result
        status   = f"{skill.icon} Query complete"

    history = history + [[user_input, reply]]
    return history, new_note, "", status

# ── Manual note save ─────────────────────────────────────
def on_save_note(note_content: str):
    write_note(note_content)
    return "💾 Note saved"

# ── Welcome message ──────────────────────────────────────
def welcome_message():
    lines = ["👋 Welcome to OmniMarkdown!\n"]
    lines.append(f"{len(SKILLS)} skill(s) loaded:\n")
    for sk in SKILLS.values():
        lines.append(f"- {sk.icon} **{sk.label}**: {sk.description}")
    lines.append("\nClick a skill button above, or type a command to get started!")
    return "\n".join(lines)

# ── Gradio UI ────────────────────────────────────────────
def build_ui():
    initial_note    = read_note()
    initial_history = [[None, welcome_message()]]

    with gr.Blocks(title="📓 OmniMarkdown") as demo:

        gr.HTML("""
        <div style="text-align:center;padding:18px 0 8px;">
            <h1 style="font-size:26px;margin:0;">📓 OmniMarkdown</h1>
            <p style="color:#64748b;margin:4px 0 0;font-size:13px;">
                AI-powered smart notebook · Low-code skill cards
            </p>
        </div>
        """)

        with gr.Row():
            # ══ Left: Chat panel ══
            with gr.Column(scale=5):
                gr.Markdown("### 💬 Chat")
                gr.Markdown("**Select a skill (auto-fills the prefix):**")

                with gr.Row():
                    skill_btns = []
                    for sid, sk in SKILLS.items():
                        btn = gr.Button(
                            f"{sk.icon} {sk.label}",
                            size="sm",
                            variant="secondary",
                        )
                        skill_btns.append((btn, sk.prefix))

                chatbot = gr.Chatbot(
                    value=initial_history,
                    label="",
                    height=400,
                    show_label=False,
                    type="tuples"  
                )

                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder="Type ? to query, or ! add / delete / modify ...",
                        show_label=False,
                        scale=8,
                        lines=1,
                        max_lines=4,
                    )
                    send_btn = gr.Button("Send ➤", variant="primary", scale=2)

                status_bar = gr.Markdown("")

            # ══ Right: Note panel ══
            with gr.Column(scale=5):
                gr.Markdown("### 📄 Note")
                note_editor = gr.Textbox(
                    value=initial_note,
                    label="",
                    lines=22,
                    max_lines=40,
                    show_label=False,
                    info="Edit directly here, then click Save to write to file",
                )
                with gr.Row():
                    save_btn    = gr.Button("💾 Save Note", variant="secondary")
                    save_status = gr.Markdown("")
                gr.Markdown("---\n**Preview:**")
                note_preview = gr.Markdown(value=initial_note)

        note_state = gr.State(initial_note)

        # ── Skill button events ──
        for btn, prefix in skill_btns:
            btn.click(
                fn=on_skill_click,
                inputs=[gr.State(prefix), user_input],
                outputs=user_input,
            )

        # ── Send events ──
        def send_and_refresh(msg, history, note):
            new_history, new_note, cleared, status = on_send(msg, history, note)
            return new_history, new_note, new_note, cleared, new_note, status

        send_btn.click(
            fn=send_and_refresh,
            inputs=[user_input, chatbot, note_state],
            outputs=[chatbot, note_state, note_editor, user_input, note_preview, status_bar],
        )
        user_input.submit(
            fn=send_and_refresh,
            inputs=[user_input, chatbot, note_state],
            outputs=[chatbot, note_state, note_editor, user_input, note_preview, status_bar],
        )

        # ── Live preview sync ──
        note_editor.change(
            fn=lambda c: (c, c),
            inputs=note_editor,
            outputs=[note_state, note_preview],
        )

        save_btn.click(
            fn=on_save_note,
            inputs=note_editor,
            outputs=save_status,
        )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,    # Set to True to generate a public link
        inbrowser=True,
    )