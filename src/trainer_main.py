"""
Main script to run the Islamic AI Trainer CLI version of the app.
This version includes additional features and functionality compared to the original.
"""

from islamic_aitrainer import IslamicAITrainer
from data_manager import DataManager
from utils import print_header, print_info, print_success, print_error
import sys
import os

def show_trainer_menu():
    """Display the trainer menu"""
    print_header("🤖 Islamic AI Fine-tuning Trainer")
    print_info("Choose an option:")
    print("1.  🚀 Start fine-tuning")
    print("2.  📊 Check job status")
    print("3.  📋 Check all jobs status")
    print("4.  🧪 Test fine-tuned model")
    print("5.  🎯 List available models")
    print("6.  📊 Prepare training data")
    print("7.  ❌ Exit")
    print("-" * 50)

def main():
    """Main application loop"""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print_error("❌ OPENAI_API_KEY environment variable not set!")
        print_info("Please set your OpenAI API key:")
        print_info("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    try:
        trainer = IslamicAITrainer()
        data_manager = DataManager()
        
        while True:
            show_trainer_menu()
            
            try:
                choice = input("Enter your choice (1-7): ").strip()
                
                if choice == '1':
                    # Start fine-tuning
                    training_file = data_manager.data_dir / "islamic_training.jsonl"
                    validation_file = data_manager.data_dir / "islamic_validation.jsonl"
                    
                    if not training_file.exists():
                        print_error("❌ No training data found! Please prepare data first (option 6)")
                        continue
                    
                    print_info(f"📁 Training file: {training_file}")
                    if validation_file.exists():
                        print_info(f"📁 Validation file: {validation_file}")
                        job_id = trainer.start_fine_tuning(str(training_file), str(validation_file))
                    else:
                        print_info("📁 No validation file found, using training data only")
                        job_id = trainer.start_fine_tuning(str(training_file))
                    
                    if job_id:
                        print_success(f"🎯 Fine-tuning started! Job ID: {job_id}")
                
                elif choice == '2':
                    # Check specific job status
                    job_id = input("Enter job ID: ").strip()
                    if job_id:
                        trainer.check_job_status(job_id)
                    else:
                        print_error("❌ Please provide a valid job ID")
                
                elif choice == '3':
                    # Check all jobs status
                    trainer.check_all_jobs_status()
                
                elif choice == '4':
                    # Test model
                    models = trainer.list_available_models()
                    if not models:
                        print_error("❌ No fine-tuned models available")
                        continue
                    
                    try:
                        choice_idx = int(input("Select model number: ").strip()) - 1
                        if 0 <= choice_idx < len(models):
                            model_name = models[choice_idx]['model_name']
                            trainer.test_model(model_name)
                        else:
                            print_error("❌ Invalid model selection")
                    except ValueError:
                        print_error("❌ Please enter a valid number")
                
                elif choice == '5':
                    # List models
                    trainer.list_available_models()
                
                elif choice == '6':
                    # Prepare training data
                    print_info("🔄 Switching to Data Manager...")
                    from main import main as data_main
                    data_main()
                
                elif choice == '7':
                    print_success("👋 Goodbye! May your AI model serve the Ummah well.")
                    break
                
                else:
                    print_error("❌ Invalid choice. Please select 1-7.")
                
                # Pause before showing menu again
                input("\nPress Enter to continue...")
                print("\n" * 2)
                
            except KeyboardInterrupt:
                print_info("\n\n🛑 Operation interrupted by user")
                continue
            except Exception as e:
                print_error(f"❌ An error occurred: {e}")
                continue
    
    except Exception as e:
        print_error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
