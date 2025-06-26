"""
JSON Training Data Validator
Helps users validate their JSON files before upload
"""

import json
from pathlib import Path

def validate_json_file(file_path):
    """Validate JSON file format for training data"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return False, "JSON must be an array/list of objects"
        
        required_fields = ['question', 'answer', 'source', 'reference']
        valid_count = 0
        issues = []
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                issues.append(f"Item {i+1}: Must be an object/dictionary")
                continue
            
            missing_fields = []
            for field in required_fields:
                if field not in item:
                    missing_fields.append(field)
                elif not item[field] or not str(item[field]).strip():
                    missing_fields.append(f"{field} (empty)")
            
            if missing_fields:
                issues.append(f"Item {i+1}: Missing fields: {', '.join(missing_fields)}")
            else:
                valid_count += 1
        
        return True, {
            'total_items': len(data),
            'valid_items': valid_count,
            'issues': issues
        }
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def create_sample_json():
    """Create a sample JSON file for users"""
    sample_data = [
        {
            "question": "What is the first pillar of Islam?",
            "answer": "The first pillar of Islam is Shahada, the declaration of faith: 'There is no god but Allah, and Muhammad is His messenger.' This is the foundation of Islamic belief.",
            "source": "Sahih al-Bukhari",
            "reference": "1",
            "category": "Pillars of Islam"
        },
        {
            "question": "What does the Quran say about seeking knowledge?",
            "answer": "The Quran emphasizes the importance of seeking knowledge. Allah says: 'And say: My Lord, increase me in knowledge.' The pursuit of knowledge is considered a form of worship.",
            "source": "Quran",
            "reference": "20:114",
            "category": "Knowledge"
        },
        {
            "question": "What is the reward for patience in Islam?",
            "answer": "Allah promises great rewards for those who are patient. The Quran states: 'And give good tidings to the patient, who, when disaster strikes them, say, Indeed we belong to Allah, and indeed to Him we will return.'",
            "source": "Quran",
            "reference": "2:155-157",
            "category": "Character"
        }
    ]
    
    output_file = Path("sample_training_data.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    return str(output_file)

if __name__ == "__main__":
    # Create sample file
    sample_file = create_sample_json()
    print(f"✅ Sample JSON created: {sample_file}")
    
    # Validate the sample
    is_valid, result = validate_json_file(sample_file)
    if is_valid:
        print(f"✅ Sample file is valid!")
        print(f"   Total items: {result['total_items']}")
        print(f"   Valid items: {result['valid_items']}")
    else:
        print(f"❌ Validation failed: {result}")
