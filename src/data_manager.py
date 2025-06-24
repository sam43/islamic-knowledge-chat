"""
Data Manager
Handles training data creation, loading, and management
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from utils import print_success, print_error, print_info, print_warning
from tabulate import tabulate
import random

class DataManager:
    def __init__(self):
        """Initialize data manager"""
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.training_file = self.data_dir / "islamic_training.jsonl"
        self.validation_file = self.data_dir / "islamic_validation.jsonl"
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)
        
        # Training data storage
        self.training_data = []
        self.validation_data = []
        
        # Load existing data if available
        self._load_existing_data()
        
        print_success("📊 Data Manager initialized")

    def _load_existing_data(self):
        """Load existing training data"""
        if self.training_file.exists():
            try:
                with open(self.training_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            self.training_data.append(json.loads(line))
                print_info(f"📥 Loaded {len(self.training_data)} existing training examples")
            except Exception as e:
                print_warning(f"⚠️ Could not load existing training data: {e}")
        
        if self.validation_file.exists():
            try:
                with open(self.validation_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            self.validation_data.append(json.loads(line))
                print_info(f"📥 Loaded {len(self.validation_data)} existing validation examples")
            except Exception as e:
                print_warning(f"⚠️ Could not load existing validation data: {e}")

    def create_training_example(self, question, answer, source, reference, category="General"):
        """Create a single training example"""
        example = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an Islamic scholar assistant specializing in Quran and the 6 Sahih Hadith collections (Bukhari, Muslim, Abu Dawood, Tirmidhi, Nasa'i, Ibn Majah). Always provide exact verse/hadith references. For non-Islamic questions, politely indicate you can search for general information."
                },
                {
                    "role": "user",
                    "content": question
                },
                {
                    "role": "assistant",
                    "content": f"{answer}\n\n**Reference:** {source} {reference}"
                }
            ],
            "category": category,
            "created_at": datetime.now().isoformat()
        }
        return example

    def generate_sample_data(self, count=30):
        """Generate sample training data"""
        sample_data = [
            {
                "question": "What are the five pillars of Islam?",
                "answer": "The five pillars of Islam are: 1) Shahada (declaration of faith) - 'There is no god but Allah, and Muhammad is His messenger', 2) Salah (five daily prayers), 3) Zakat (obligatory charity), 4) Sawm (fasting during Ramadan), and 5) Hajj (pilgrimage to Mecca for those who are able). These form the foundation of Muslim practice.",
                "source": "Sahih al-Bukhari",
                "reference": "8",
                "category": "Pillars of Islam"
            },
            {
                "question": "What does the Quran say about prayer?",
                "answer": "The Quran emphasizes prayer throughout. Allah says: 'And establish prayer and give zakah and bow with those who bow.' Prayer is described as a direct connection between the believer and Allah, to be performed at prescribed times with devotion and humility.",
                "source": "Quran",
                "reference": "2:43",
                "category": "Prayer"
            },
            {
                "question": "What is the importance of charity in Islam?",
                "answer": "Charity (Zakat) is one of the five pillars of Islam. The Quran states: 'And establish prayer and give zakat, and whatever good you put forward for yourselves - you will find it with Allah. Indeed, Allah of what you do, is Seeing.' It purifies wealth and helps the needy.",
                "source": "Quran",
                "reference": "2:110",
                "category": "Charity"
            },
            {
                "question": "What did Prophet Muhammad say about kindness to parents?",
                "answer": "The Prophet (peace be upon him) emphasized the importance of being kind to parents. He said: 'Paradise lies at the feet of your mother.' He also said that being dutiful to parents is among the best deeds, ranking right after prayer offered on time.",
                "source": "Sunan an-Nasa'i",
                "reference": "3104",
                "category": "Family Relations"
            },
            {
                "question": "What is the reward for reciting the Quran?",
                "answer": "The Prophet (peace be upon him) said: 'Whoever reads a letter from the Book of Allah, he will have a reward, and this reward will be multiplied by ten. I do not say that Alif-Lam-Meem is a letter, rather I say that Alif is a letter, Lam is a letter and Meem is a letter.'",
                "source": "Jami` at-Tirmidhi",
                "reference": "2910",
                "category": "Quran Recitation"
            },
            {
                "question": "What does the Quran say about patience?",
                "answer": "The Quran frequently mentions patience (Sabr) as a virtue. Allah says: 'And give good tidings to the patient, Who, when disaster strikes them, say, \"Indeed we belong to Allah, and indeed to Him we will return.\"' Patience is rewarded without measure.",
                "source": "Quran",
                "reference": "2:155-156",
                "category": "Character"
            },
            {
                "question": "What is the best day according to Islam?",
                "answer": "The Prophet (peace be upon him) said: 'The best day on which the sun has risen is Friday; on it Adam was created, on it he was made to enter Paradise, on it he was expelled from it, and the Hour will take place on no other day than Friday.'",
                "source": "Sahih Muslim",
                "reference": "854",
                "category": "Time and Days"
            },
            {
                "question": "What does Islam say about honesty?",
                "answer": "The Prophet (peace be upon him) said: 'Truthfulness leads to righteousness, and righteousness leads to Paradise. A man keeps on telling the truth until he becomes a truthful person. Falsehood leads to wickedness, and wickedness leads to Hell.'",
                "source": "Sahih al-Bukhari",
                "reference": "6094",
                "category": "Character"
            },
            {
                "question": "How should I respond to non-Islamic questions?",
                "answer": "I specialize in Islamic knowledge from the Quran and authentic Hadiths. For questions outside Islamic teachings, I can help search for accurate information to assist you. My primary expertise is in matters of faith, Islamic law, and guidance from our sacred texts.",
                "source": "System Guidance",
                "reference": "Scope Definition",
                "category": "System Behavior"
            },
            {
                "question": "What's the weather like today?",
                "answer": "I'm an Islamic knowledge assistant specializing in Quran and Hadith teachings. For current weather information, I'd be happy to help you search for local weather updates. My expertise is primarily in Islamic guidance and religious knowledge.",
                "source": "System Guidance",
                "reference": "Scope Redirection",
                "category": "System Behavior"
            }
        ]
        
        # Generate more examples by cycling through the base set
        generated_count = 0
        base_count = len(sample_data)
        
        while generated_count < count:
            for base_example in sample_data:
                if generated_count >= count:
                    break
                
                example = self.create_training_example(
                    base_example["question"],
                    base_example["answer"],
                    base_example["source"],
                    base_example["reference"],
                    base_example["category"]
                )
                
                self.training_data.append(example)
                generated_count += 1
        
        self._save_training_data()
        print_success(f"✅ Generated {count} training examples")

    def manual_data_entry(self):
        """Manual training data entry"""
        print_info("✏️ Manual Training Data Entry")
        print_info("Enter 'quit' for any field to stop entry")
        
        while True:
            try:
                print_info("\n" + "="*50)
                question = input("📝 Question: ").strip()
                if question.lower() == 'quit':
                    break
                
                answer = input("💬 Answer: ").strip()
                if answer.lower() == 'quit':
                    break
                
                source = input("📚 Source (e.g., 'Quran', 'Sahih al-Bukhari'): ").strip()
                if source.lower() == 'quit':
                    break
                
                reference = input("🔖 Reference (e.g., '2:110', '6094'): ").strip()
                if reference.lower() == 'quit':
                    break
                
                category = input("🏷️ Category (optional): ").strip() or "General"
                if category.lower() == 'quit':
                    break
                
                # Create and add example
                example = self.create_training_example(question, answer, source, reference, category)
                self.training_data.append(example)
                
                print_success("✅ Example added successfully!")
                
                continue_entry = input("➕ Add another example? (y/n): ").strip().lower()
                if continue_entry != 'y':
                    break
                    
            except KeyboardInterrupt:
                print_info("\n🛑 Manual entry stopped")
                break
        
        if self.training_data:
            self._save_training_data()
            print_success(f"💾 Saved {len(self.training_data)} training examples")

    def load_from_template(self):
        """Load data from a template file"""
        template_file = self.data_dir / "template.json"
        
        if not template_file.exists():
            self._create_template_file()
            print_info(f"📝 Template created at: {template_file}")
            print_info("Please edit the template file and run this option again")
            return
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            for item in template_data:
                example = self.create_training_example(
                    item["question"],
                    item["answer"],
                    item["source"],
                    item["reference"],
                    item.get("category", "General")
                )
                self.training_data.append(example)
            
            self._save_training_data()
            print_success(f"✅ Loaded {len(template_data)} examples from template")
            
        except Exception as e:
            print_error(f"❌ Failed to load template: {e}")

    def _create_template_file(self):
        """Create a template file for easy data entry"""
        template = [
            {
                "question": "What is the first pillar of Islam?",
                "answer": "The first pillar of Islam is Shahada, the declaration of faith: 'There is no god but Allah, and Muhammad is His messenger.' This is the foundation of Islamic belief.",
                "source": "Sahih al-Bukhari",
                "reference": "1",
                "category": "Pillars of Islam"
            },
            {
                "question": "Add your question here",
                "answer": "Add your answer here",
                "source": "Quran or Hadith collection name",
                "reference": "Verse or hadith number",
                "category": "Category name (optional)"
            }
        ]
        
        template_file = self.data_dir / "template.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

    def load_from_csv(self, csv_file_path):
        """Load data from CSV file"""
        csv_path = Path(csv_file_path)
        if not csv_path.exists():
            print_error(f"❌ CSV file not found: {csv_file_path}")
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                loaded_count = 0
                
                for row in reader:
                    if all(key in row for key in ['question', 'answer', 'source', 'reference']):
                        example = self.create_training_example(
                            row['question'],
                            row['answer'],
                            row['source'],
                            row['reference'],
                            row.get('category', 'General')
                        )
                        self.training_data.append(example)
                        loaded_count += 1
                    else:
                        print_warning(f"⚠️ Skipping row with missing required fields: {row}")
                
                self._save_training_data()
                print_success(f"✅ Loaded {loaded_count} examples from CSV")
                
        except Exception as e:
            print_error(f"❌ Failed to load CSV: {e}")

    def export_to_csv(self, output_file="training_data_export.csv"):
        """Export training data to CSV"""
        if not self.training_data:
            print_warning("⚠️ No training data to export")
            return
        
        output_path = self.data_dir / output_file
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['question', 'answer', 'source', 'reference', 'category', 'created_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for example in self.training_data:
                    messages = example['messages']
                    writer.writerow({
                        'question': messages[1]['content'],
                        'answer': messages[2]['content'].split('\n\n**Reference:**')[0],
                        'source': messages[2]['content'].split('**Reference:** ')[1] if '**Reference:**' in messages[2]['content'] else '',
                        'reference': '',
                        'category': example.get('category', 'General'),
                        'created_at': example.get('created_at', '')
                    })
            
            print_success(f"✅ Exported {len(self.training_data)} examples to {output_path}")
            
        except Exception as e:
            print_error(f"❌ Failed to export CSV: {e}")

    def split_train_validation(self, validation_ratio=0.2):
        """Split data into training and validation sets"""
        if not self.training_data:
            print_warning("⚠️ No training data to split")
            return
        
        # Shuffle data
        shuffled_data = self.training_data.copy()
        random.shuffle(shuffled_data)
        
        # Calculate split point
        total_count = len(shuffled_data)
        validation_count = int(total_count * validation_ratio)
        train_count = total_count - validation_count
        
        # Split data
        self.validation_data = shuffled_data[:validation_count]
        self.training_data = shuffled_data[validation_count:]
        
        # Save both sets
        self._save_training_data()
        self._save_validation_data()
        
        print_success(f"✅ Split data: {train_count} training, {validation_count} validation examples")

    def _save_training_data(self):
        """Save training data to JSONL file"""
        try:
            with open(self.training_file, 'w', encoding='utf-8') as f:
                for example in self.training_data:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
            print_info(f"💾 Saved {len(self.training_data)} training examples")
        except Exception as e:
            print_error(f"❌ Failed to save training data: {e}")

    def _save_validation_data(self):
        """Save validation data to JSONL file"""
        try:
            with open(self.validation_file, 'w', encoding='utf-8') as f:
                for example in self.validation_data:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
            print_info(f"💾 Saved {len(self.validation_data)} validation examples")
        except Exception as e:
            print_error(f"❌ Failed to save validation data: {e}")

    def validate_data_format(self):
        """Validate training data format for OpenAI fine-tuning"""
        if not self.training_data:
            print_warning("⚠️ No training data to validate")
            return False
        
        valid_count = 0
        issues = []
        
        for i, example in enumerate(self.training_data):
            try:
                # Check required structure
                if 'messages' not in example:
                    issues.append(f"Example {i}: Missing 'messages' field")
                    continue
                
                messages = example['messages']
                if len(messages) != 3:
                    issues.append(f"Example {i}: Should have exactly 3 messages (system, user, assistant)")
                    continue
                
                # Check message roles
                expected_roles = ['system', 'user', 'assistant']
                for j, msg in enumerate(messages):
                    if 'role' not in msg or 'content' not in msg:
                        issues.append(f"Example {i}, Message {j}: Missing 'role' or 'content'")
                        continue
                    
                    if msg['role'] != expected_roles[j]:
                        issues.append(f"Example {i}, Message {j}: Expected role '{expected_roles[j]}', got '{msg['role']}'")
                        continue
                
                valid_count += 1
                
            except Exception as e:
                issues.append(f"Example {i}: Validation error - {e}")
        
        # Print validation results
        print_info(f"📊 Validation Results:")
        print_info(f"   Valid examples: {valid_count}/{len(self.training_data)}")
        
        if issues:
            print_warning(f"⚠️ Found {len(issues)} issues:")
            for issue in issues[:10]:  # Show first 10 issues
                print_warning(f"   - {issue}")
            if len(issues) > 10:
                print_warning(f"   ... and {len(issues) - 10} more issues")
        else:
            print_success("✅ All training data is valid!")
        
        return len(issues) == 0

    def get_statistics(self):
        """Get statistics about the training data"""
        if not self.training_data:
            print_warning("⚠️ No training data available")
            return
        
        # Category distribution
        categories = {}
        total_chars = 0
        total_tokens_estimate = 0
        
        for example in self.training_data:
            category = example.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            # Estimate character and token counts
            for message in example['messages']:
                content = message['content']
                total_chars += len(content)
                total_tokens_estimate += len(content.split()) * 1.3  # Rough token estimate
        
        # Create statistics table
        stats_data = [
            ["Total Examples", len(self.training_data)],
            ["Validation Examples", len(self.validation_data)],
            ["Total Characters", f"{total_chars:,}"],
            ["Estimated Tokens", f"{int(total_tokens_estimate):,}"],
            ["Average Chars/Example", f"{total_chars // len(self.training_data):,}"]
        ]
        
        print_info("📊 Training Data Statistics:")
        print(tabulate(stats_data, headers=["Metric", "Value"], tablefmt="grid"))
        
        # Category distribution
        if categories:
            print_info("\n📂 Category Distribution:")
            category_data = [[cat, count, f"{count/len(self.training_data)*100:.1f}%"] 
                           for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)]
            print(tabulate(category_data, headers=["Category", "Count", "Percentage"], tablefmt="grid"))

    def clean_data(self):
        """Clean and deduplicate training data"""
        if not self.training_data:
            print_warning("⚠️ No training data to clean")
            return
        
        original_count = len(self.training_data)
        
        # Remove duplicates based on question content
        seen_questions = set()
        cleaned_data = []
        
        for example in self.training_data:
            question = example['messages'][1]['content'].strip().lower()
            if question not in seen_questions:
                seen_questions.add(question)
                cleaned_data.append(example)
        
        self.training_data = cleaned_data
        removed_count = original_count - len(cleaned_data)
        
        if removed_count > 0:
            self._save_training_data()
            print_success(f"✅ Removed {removed_count} duplicate examples")
        else:
            print_info("ℹ️ No duplicates found")

    def backup_data(self):
        """Create a backup of current training data"""
        if not self.training_data:
            print_warning("⚠️ No training data to backup")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.data_dir / f"backup_training_{timestamp}.jsonl"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                for example in self.training_data:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
            
            print_success(f"✅ Backup created: {backup_file}")
            
        except Exception as e:
            print_error(f"❌ Failed to create backup: {e}")

    def clear_all_data(self):
        """Clear all training data (with confirmation)"""
        if not self.training_data:
            print_info("ℹ️ No training data to clear")
            return
        
        confirm = input(f"⚠️ Are you sure you want to delete all {len(self.training_data)} training examples? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            self.training_data = []
            self.validation_data = []
            
            # Remove files
            if self.training_file.exists():
                self.training_file.unlink()
            if self.validation_file.exists():
                self.validation_file.unlink()
            
            print_success("✅ All training data cleared")
        else:
            print_info("ℹ️ Operation cancelled")

    def preview_examples(self, count=3):
        """Preview a few training examples"""
        if not self.training_data:
            print_warning("⚠️ No training data to preview")
            return
        
        preview_count = min(count, len(self.training_data))
        print_info(f"👀 Previewing {preview_count} training examples:")
        
        for i in range(preview_count):
            example = self.training_data[i]
            messages = example['messages']
            
            print_info(f"\n{'='*60}")
            print_info(f"Example {i+1} - Category: {example.get('category', 'Unknown')}")
            print_info(f"{'='*60}")
            print_info(f"🤖 System: {messages[0]['content'][:100]}...")
            print_info(f"👤 User: {messages[1]['content']}")
            print_info(f"🤖 Assistant: {messages[2]['content']}")
