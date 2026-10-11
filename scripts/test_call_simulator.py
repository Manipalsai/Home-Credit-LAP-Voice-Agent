import sys
import os
import uuid

# Ensure backend in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.conversation_service import conversation_service


def main():
    print("=" * 70)
    print(" HOME CREDIT LAP — LOCAL CALL SIMULATOR (CLI)")
    print(" Type 'quit' or 'exit' to stop the call simulation.")
    print("=" * 70)

    customer_name = input("Enter simulated customer name [default: Rajesh Sharma]: ").strip() or "Rajesh Sharma"
    session_id = f"cli_{uuid.uuid4().hex[:8]}"

    greeting = conversation_service.get_initial_greeting(session_id, customer_name)
    print(f"\n[AI Voice Agent]: {greeting}")

    while True:
        try:
            user_input = input("\n[Customer]: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit"]:
                print("\nSimulation ended by operator.")
                break

            response, state, facts = conversation_service.process_turn(session_id, user_input)
            print(f"\n[AI Voice Agent]: {response}")
            print(f"  └─ Stage: {state.stage.value} | Outcome: {state.outcome.value} | Terminal: {state.is_terminal}")
            if facts:
                print(f"  └─ Extracted Facts: {facts}")

            if state.is_terminal:
                print(f"\n[Call Ended with Terminal Outcome: {state.outcome.value}]")
                break

        except (KeyboardInterrupt, EOFError):
            print("\nSimulation aborted.")
            break


if __name__ == "__main__":
    main()
