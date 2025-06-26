# 🌐 Gradio Web Interface for Islamic AI Fine-tuning

A user-friendly web interface for training AI models on Islamic knowledge.

## 🚀 Quick Start

### Option 1: Using the launch script
\`\`\`bash
chmod +x run_gradio.sh
./run_gradio.sh
\`\`\`

### Option 2: Manual setup
\`\`\`bash
# Install requirements
pip install -r requirements.txt

# Set OpenAI API key (optional for data management)
export OPENAI_API_KEY='your-openai-api-key'

# Launch interface
python launch_gradio.py
\`\`\`

## 🎯 Features

### 📊 Data Management
- **File Upload**: Upload JSON and TXT files for training data
- **Web Scraping**: Extract content from websites automatically
- **Manual Entry**: Add training examples through web forms
- **Sample Generation**: Create sample Islamic Q&A data

### 📈 Data Statistics
- **Real-time Stats**: View training data statistics
- **Data Validation**: Check format compatibility
- **Train/Validation Split**: Prepare data for training
- **Export Options**: Download data as CSV

### 🚀 Model Training
- **One-click Training**: Start fine-tuning with OpenAI
- **Progress Monitoring**: Check training job status
- **Model Management**: List and organize trained models

### 🧪 Model Testing
- **Interactive Testing**: Test models with custom questions
- **Islamic Knowledge**: Specialized for Quran and Hadith
- **Response Evaluation**: Review model performance

## 📱 Interface Sections

### 1. Data Management Tab
- Upload JSON/TXT files
- Scrape websites for content
- Add manual training examples
- Generate sample data

### 2. Data Statistics Tab
- View current data overview
- Split data for training/validation
- Validate data format
- Export data to CSV

### 3. Model Training Tab
- Start fine-tuning process
- Monitor training progress
- Check job status

### 4. Model Testing Tab
- List available models
- Test models interactively
- Evaluate responses

## 🌐 Web Scraping Features

The web scraper can:
- Extract content from any website
- Handle multiple pages
- Clean and format text
- Save content to files
- Respect website policies with delays

### Supported Content Types
- HTML pages
- Articles and blog posts
- Islamic educational content
- Q&A websites
- Documentation sites

## 📁 File Formats

### JSON Training Data Format
\`\`\`json
[
  {
    "question": "What are the five pillars of Islam?",
    "answer": "The five pillars are...",
    "source": "Sahih al-Bukhari",
    "reference": "8",
    "category": "Pillars of Islam"
  }
]
\`\`\`

### Text File Processing
- Automatically saved to `scraped_content/` directory
- Manual processing required for Q&A extraction
- Can be used as reference material

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for training features
- `GRADIO_SERVER_PORT`: Custom port (default: 7860)

### Directory Structure
\`\`\`
project/
├── data/                 # Training data files
├── scraped_content/      # Web scraped content
├── logs/                 # Training logs
├── models/               # Model information
└── gradio_app.py         # Main interface
\`\`\`

## 🛡️ Security & Ethics

- **Respectful Scraping**: Includes delays between requests
- **Content Validation**: Manual review recommended
- **Islamic Authenticity**: Verify all religious content
- **Privacy**: No data sent to external services (except OpenAI for training)

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   \`\`\`bash
   # Change port in launch_gradio.py
   interface.launch(server_port=7861)
   \`\`\`

2. **Missing Dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **OpenAI API Issues**
   - Verify API key is set correctly
   - Check API quota and billing
   - Ensure key has fine-tuning permissions

4. **Web Scraping Blocked**
   - Some sites block automated requests
   - Try different URLs or manual content entry
   - Respect robots.txt and terms of service

## 📞 Support

For issues or questions:
1. Check the console output for error messages
2. Verify all requirements are installed
3. Ensure OpenAI API key is valid
4. Review scraped content for quality

---

*May this tool serve the Ummah in spreading authentic Islamic knowledge through AI.*
