# 🕌 Noor-AI: An Islamic Knowledge-Based AI Model and Fine-tuning Project Overview

## 🎯 **Project Goal**

Create a comprehensive platform for fine-tuning AI models specifically on **authentic Islamic knowledge** from the Quran and the 6 Sahih Hadith collections (Bukhari, Muslim, Abu Dawood, Tirmidhi, Nasa'i, Ibn Majah).

## 🏗️ **Core Architecture**

### **📊 Data Management System**

- **Multiple Input Methods**: JSON, TXT, PDF file uploads + web scraping
- **AI-Powered Processing**: Converts raw content into structured Q&A training data
- **Quality Validation**: Ensures proper Islamic sources and references
- **Smart Filtering**: Distinguishes between Islamic content and general information


### **🌐 Web Scraping Engine**

- **AI-Enhanced Extraction**: Uses OpenAI to filter quality content from gibberish
- **Islamic Content Detection**: Keyword + AI-based identification of religious content
- **Source Validation**: Toggle for requiring authentic Islamic sources
- **Respectful Scraping**: Proper delays and error handling


### **🤖 Training Pipeline**

- **OpenAI Integration**: Direct fine-tuning using OpenAI's API
- **Progress Monitoring**: Real-time job status tracking
- **Model Management**: Organize and test multiple fine-tuned models
- **Validation Support**: Train/validation data splitting


### **🖥️ User Interface**

- **Gradio Web Interface**: User-friendly web-based platform
- **Multi-Tab Organization**: Data management, statistics, training, testing
- **Real-time Feedback**: Live statistics and progress updates
- **File Management**: Upload, preview, and process various file formats


## 🎯 **Key Features**

### **📚 Data Sources**

1. **File Uploads**: JSON (structured), TXT (raw text), PDF (documents)
2. **Web Scraping**: Automatic extraction from Islamic websites
3. **Manual Entry**: Direct Q&A input with source validation
4. **Sample Generation**: Pre-built Islamic knowledge examples


### **🔍 Content Processing**

- **AI Quality Analysis**: Determines educational value vs noise
- **Islamic Source Toggle**: Enforces authentic source requirements
- **Reference Extraction**: Automatically finds Quran verses and Hadith numbers
- **Category Organization**: Groups content by Islamic topics


### **🚀 Training Workflow**

```plaintext
Data Input → AI Processing → Quality Validation → Training Data → Fine-tuning → Model Testing
```

## 🎯 **Target Use Cases**

### **🕌 Islamic Education**

- Train models to answer questions about Islamic practices
- Provide authentic Quran and Hadith references
- Maintain scholarly accuracy in responses


### **📖 Knowledge Preservation**

- Digitize Islamic educational content
- Create searchable Q&A databases
- Preserve traditional Islamic scholarship


### **🤖 AI Specialization**

- Fine-tune general AI models for Islamic knowledge
- Ensure responses include proper source citations
- Handle both Islamic and general queries appropriately


## 🛡️ **Quality Assurance**

### **📋 Data Validation**

- **Required Fields**: Question, Answer, Source, Reference
- **Format Compliance**: OpenAI fine-tuning compatibility
- **Source Authenticity**: Verification of Islamic references


### **🔍 Content Filtering**

- **AI-Powered**: Distinguishes quality content from ads/navigation
- **Islamic Detection**: Identifies religious vs general content
- **Confidence Scoring**: Provides reliability metrics


## 🎯 **Project Benefits**

### **For Islamic Scholars**

- Digitize and organize Islamic knowledge
- Create AI assistants for Islamic education
- Maintain authentic source references


### **For Developers**

- Complete fine-tuning pipeline
- Web scraping with AI enhancement
- Ready-to-use training infrastructure


### **For the Community**

- Accessible Islamic knowledge through AI
- Authentic source preservation
- Educational tool development


## 🚀 **Technical Stack**

- **Backend**: Python, OpenAI API, BeautifulSoup, Pandas
- **Frontend**: Gradio web interface
- **AI**: GPT-4o-mini for content processing and fine-tuning
- **Data**: JSONL format for training, CSV for export
- **Storage**: Local file system with organized directories


## 🎯 **Current Status**

The project provides a **complete end-to-end solution** for creating specialized Islamic AI models, from data collection through training to testing, with both technical sophistication and respect for Islamic scholarship traditions.

---

*"May this project serve the Ummah in preserving and sharing authentic Islamic knowledge through modern AI technology."* 🕌✨
