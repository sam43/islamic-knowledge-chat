"""
Main script to run the Islamic AI Fine-tuning Data Manager
"""

from data_manager import DataManager
from utils import print_header, print_info, print_success, print_error
import sys

def show_menu():
    """Display the main menu"""
    print_header("🕌 Islamic AI Fine-tuning Data Manager")
    print_info("Choose an option:")
    print("1.  📊 View data statistics")
    print("2.  👀 Preview training examples")
    print("3.  ✏️  Manual data entry")
    print("4.  🎲 Generate sample data")
    print("5.  📝 Load from template")
    print("6.  📄 Load from CSV")
    print("7.  💾 Export to CSV")
    print("8.  ✂️  Split train/validation")
    print("9.  🔍 Validate data format")
    print("10. 🧹 Clean data (remove duplicates)")
    print("11. 💾 Backup data")
    print("12. 🗑️  Clear all data")
    print("13. ❌ Exit")
    print("-" * 50)

def main():
    """Main application loop"""
    try:
        # Initialize data manager
        dm = DataManager()
        
        while True:
            show_menu()
            
            try:
                choice = input("Enter your choice (1-13): ").strip()
                
                if choice == '1':
                    dm.get_statistics()
                
                elif choice == '2':
                    count = input("How many examples to preview? (default: 3): ").strip()
                    count = int(count) if count.isdigit() else 3
                    dm.preview_examples(count)
                
                elif choice == '3':
                    dm.manual_data_entry()
                
                elif choice == '4':
                    count = input("How many sample examples to generate? (default: 30): ").strip()
                    count = int(count) if count.isdigit() else 30
                    dm.generate_sample_data(count)
                
                elif choice == '5':
                    dm.load_from_template()
                
                elif choice == '6':
                    csv_path = input("Enter CSV file path: ").strip()
                    if csv_path:
                        dm.load_from_csv(csv_path)
                    else:
                        print_error("❌ Please provide a valid CSV file path")
                
                elif choice == '7':
                    filename = input("Enter output filename (default: training_data_export.csv): ").strip()
                    filename = filename if filename else "training_data_export.csv"
                    dm.export_to_csv(filename)
                
                elif choice == '8':
                    ratio = input("Enter validation ratio (default: 0.2): ").strip()
                    try:
                        ratio = float(ratio) if ratio else 0.2
                        if 0 < ratio < 1:
                            dm.split_train_validation(ratio)
                        else:
                            print_error("❌ Validation ratio must be between 0 and 1")
                    except ValueError:
                        print_error("❌ Invalid ratio format")
                
                elif choice == '9':
                    dm.validate_data_format()
                
                elif choice == '10':
                    dm.clean_data()
                
                elif choice == '11':
                    dm.backup_data()
                
                elif choice == '12':
                    dm.clear_all_data()
                
                elif choice == '13':
                    print_success("👋 Goodbye! May your AI model serve the Ummah well.")
                    break
                
                else:
                    print_error("❌ Invalid choice. Please select 1-13.")
                
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
