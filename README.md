# 🕌 Islamic AI Fine-tuning Project

A comprehensive system for fine-tuning AI models on Islamic knowledge from the Quran and authentic Hadiths.

## 🎯 Features

- **Data Management**: Create, organize, and validate training data
- **Fine-tuning**: Train models using OpenAI's API
- **Testing**: Evaluate model performance with Islamic Q&A
- **Monitoring**: Track training jobs and model status

## 🚀 Quick Start

1. **Setup Environment**:
   \`\`\`bash
   chmod +x setup.sh
   ./setup.sh
   \`\`\`

2. **Set API Key**:
   \`\`\`bash
   export OPENAI_API_KEY='your-openai-api-key'
   \`\`\`

3. **Prepare Data**:
   \`\`\`bash
   python main.py
   \`\`\`

4. **Start Training**:
   \`\`\`bash
   python trainer_main.py
   \`\`\`

## 📁 Project Structure

\`\`\`
islamic-ai-finetuning/
├── data_manager.py      # Data management system
├── islamic_aitrainer.py # Fine-tuning operations
├── utils.py            # Utility functions
├── main.py             # Data manager interface
├── trainer_main.py     # Training interface
├── requirements.txt    # Dependencies
├── setup.sh           # Setup script
├── data/              # Training data
├── logs/              # Training logs
└── models/            # Model information
\`\`\`

## 🔧 Usage

### Data Management
- Generate sample Islamic Q&A data
- Manual data entry with validation
- Import from CSV/JSON templates
- Export and backup capabilities

### Fine-tuning
- Upload data to OpenAI
- Start fine-tuning jobs
- Monitor training progress
- Test completed models

## 📊 Data Format

Training examples follow OpenAI's chat format:
\`\`\`json
{
  "messages": [
    {"role": "system", "content": "Islamic scholar assistant..."},
    {"role": "user", "content": "What are the five pillars of Islam?"},
    {"role": "assistant", "content": "The five pillars are... **Reference:** Sahih al-Bukhari 8"}
  ]
}
\`\`\`

## 🤝 Contributing

1. Ensure all Islamic content is authentic and properly referenced
2. Follow the existing code structure and documentation
3. Test thoroughly before submitting changes

## 📜 License

This project is intended for educational and religious purposes. Please use responsibly and ensure all Islamic content is accurate and properly attributed.

---

*May this project serve the Ummah and help spread authentic Islamic knowledge.*
