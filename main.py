"""
╔══════════════════════════════════════════════════════════════╗
║             🤖 AUTO-ANALYST AI — Main Entry Point            ║
║        Autonomous Data Analysis Agent powered by LangGraph   ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python main.py
    
    Then follow the interactive prompts:
    1. Enter path to your CSV file
    2. Ask your analysis question in plain English
    3. The agent will Profile → Plan → Code → Execute → Answer
"""

import os
import sys
from src.graph import app


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DISPLAY FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_banner():
    """Prints the welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🤖  A U T O - A N A L Y S T   A I  🤖                ║
║                                                              ║
║   Your Autonomous Data Analysis Agent                        ║
║   ─────────────────────────────────────                      ║
║   📄 Give me a CSV file                                      ║
║   💬 Ask me anything about your data                         ║
║   ⚡ I'll write code, run it, and give you answers           ║
║                                                              ║
║   Powered by: LangGraph • Llama 3.3 • Pandas                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_separator():
    print("\n" + "━" * 60)


def print_result(final_state: dict):
    """Displays the final output after graph execution."""
    print_separator()
    print("📊  ANALYSIS COMPLETE")
    print_separator()
    
    # Show Final Answer
    answer = final_state.get("final_answer")
    if answer:
        print(f"\n{answer}")
    else:
        # If insight node didn't run (e.g., data loading failed)
        error = final_state.get("error")
        if error:
            print(f"\n❌ Analysis could not be completed.\nReason: {error}")
        else:
            print("\n⚠️ No insights were generated.")
    
    # Show Image Path
    image_path = final_state.get("image_path", "output.png")
    if os.path.exists(image_path):
        abs_path = os.path.abspath(image_path)
        print(f"\n📈 Chart saved at: {abs_path}")
    
    # Show Code (truncated)
    code = final_state.get("python_code")
    if code:
        print(f"\n💻 Generated Code ({len(code)} chars):")
        print("─" * 40)
        # Show first 500 chars
        preview = code[:500] + ("..." if len(code) > 500 else "")
        print(preview)
        print("─" * 40)
    
    print_separator()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN FUNCTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_agent():
    """Interactive loop for the Auto-Analyst AI agent."""
    print_banner()
    
    # Step 1: Get CSV path
    while True:
        csv_path = input("📂 Enter CSV file path (or 'quit' to exit): ").strip()
        
        if csv_path.lower() in ('quit', 'exit', 'q'):
            print("\n👋 Goodbye! Thank you for using Auto-Analyst AI.")
            return
        
        # Remove quotes if user wraps path in quotes
        csv_path = csv_path.strip('"').strip("'")
        
        if not os.path.exists(csv_path):
            print(f"❌ File not found: '{csv_path}'. Please try again.\n")
            continue
        
        if not csv_path.lower().endswith(('.csv', '.CSV')):
            print("⚠️ Warning: File doesn't appear to be a CSV. Proceeding anyway...\n")
        
        print(f"✅ File loaded: {os.path.basename(csv_path)}")
        break
    
    # Step 2: Query Loop (multiple questions on same dataset)
    while True:
        print_separator()
        query = input("\n💬 Ask your question (or 'change' for new file, 'quit' to exit):\n➤ ").strip()
        
        if query.lower() in ('quit', 'exit', 'q'):
            print("\n👋 Goodbye! Thank you for using Auto-Analyst AI.")
            return
        
        if query.lower() in ('change', 'new', 'switch'):
            print("\n🔄 Switching to new dataset...\n")
            run_agent()  # Restart
            return
        
        if not query:
            print("⚠️ Please enter a valid question.")
            continue
        
        # Step 3: Run the Agent
        print(f"\n🚀 Starting Analysis Pipeline...")
        print(f"   📄 File: {os.path.basename(csv_path)}")
        print(f"   💬 Query: {query}")
        print_separator()
        
        initial_state = {
            "csv_file_path": csv_path,
            "user_query": query,
            "revision_count": 0,
            "messages": []
        }
        
        try:
            # Stream execution — show progress in real-time
            final_state = {}
            for output in app.stream(initial_state):
                for node_name, state_update in output.items():
                    print(f"\n  ✅ Completed: {node_name}")
                    
                    if state_update is None:
                        continue
                    
                    # Merge state updates
                    final_state.update(state_update)
                    
                    if state_update.get("error"):
                        print(f"  ⚠️ Error: {state_update['error'][:100]}...")
            
            # Display Results
            print_result(final_state)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Analysis cancelled by user.")
        except Exception as e:
            print(f"\n❌ System Error: {e}")
            print("   Please check your API keys and try again.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    run_agent()
