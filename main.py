from orchestrator import run_task

def print_result(result):
    """Simple, clean result display."""
    if result["status"] == "success":
        print("\n" + "="*60)
        print("✅ COMPLETE")
        print("="*60)
        
        # Show project info if created
        if result.get("project_path"):
            print(f"\n📁 Project: {result['project_path']}")
            if result.get("saved_files"):
                print(f"📄 Files: {', '.join(result['saved_files'])}")
        
        print("\n" + "="*60 + "\n")
        
    elif result["status"] == "error":
        print("\n" + "="*60)
        print("❌ ERROR")
        print("="*60)
        print(result.get("message", "Unknown error"))
        print("="*60 + "\n")

def main():
    print("="*60)
    print("🤖 AI Agent System")
    print("="*60)
    print("Enter your task. Type 'exit' to quit.\n")
    
    while True:
        try:
            task = input("📝 Task: ").strip()
            
            if not task:
                continue
                
            if task.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!\n")
                break

            print()  # Empty line before processing
            
            result = run_task(task)
            print_result(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            if input("Continue? (y/n): ").lower() != 'y':
                break

if __name__ == "__main__":
    main()
