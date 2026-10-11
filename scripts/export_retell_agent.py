import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.voice.retell_adapter import retell_adapter


def main():
    print("=" * 70)
    print(" RETELL AI AGENT CONFIGURATION EXPORTER")
    print("=" * 70)

    config = retell_adapter.export_agent_config()
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompts", "retell_agent_schema.json"))

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"\nSuccessfully generated Retell AI agent creation configuration:")
    print(f"Path: {out_path}\n")
    print(f"Agent Name: {config['agent_name']}")
    print(f"Voice ID: {config['voice_id']}")
    print(f"Language: {config['language']}")
    print(f"Dynamic Variables: {', '.join(config['dynamic_variables'])}")
    print(f"\nYou can paste this payload directly into Retell AI API: POST https://api.retellai.com/create-agent")


if __name__ == "__main__":
    main()
