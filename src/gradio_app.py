"""
Gradio Web Interface for Islamic AI Fine-tuning Project
"""

import gradio as gr
import json
import os
import time
from pathlib import Path
from datetime import datetime
from data_manager import DataManager
from islamic_aitrainer import IslamicAITrainer
from web_scraper import WebScraper
from utils import print_success, print_error, print_info, print_warning
import pandas as pd
import PyPDF2
import pdfplumber
from openai import OpenAI

class GradioApp:
    def __init__(self):
        """Initialize the Gradio application"""
        self.data_manager = DataManager()
        self.trainer = None
        self.web_scraper = WebScraper()
        
        # Initialize trainer only if API key is available
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.trainer = IslamicAITrainer()
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except Exception as e:
                print_warning(f"⚠️ Could not initialize trainer: {e}")
        
        self.project_root = Path(__file__).parent
        self.scraped_dir = self.project_root / "scraped_content"
        self.scraped_dir.mkdir(exist_ok=True)

    def extract_pdf_text(self, pdf_path):
        """Extract text from PDF file using multiple methods"""
        text_content = ""
        
        try:
            # Method 1: Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n\n"
            
            if text_content.strip():
                return text_content
                
        except Exception as e:
            print_warning(f"⚠️ pdfplumber failed: {e}")
        
        try:
            # Method 2: Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n\n"
                        
        except Exception as e:
            print_warning(f"⚠️ PyPDF2 failed: {e}")
            return None
        
        return text_content if text_content.strip() else None

    def process_text_with_ai(self, text_content, islamic_sources_required=False):
        """Process text content using OpenAI to extract Q&A pairs"""
        if not self.openai_client:
            return {
                'success': False,
                'message': 'OpenAI client not available. Please set OPENAI_API_KEY.',
                'qa_pairs': []
            }
        
        try:
            # Split text into chunks if too long
            max_chunk_size = 8000  # Leave room for prompt
            text_chunks = []
            
            if len(text_content) > max_chunk_size:
                words = text_content.split()
                current_chunk = []
                current_size = 0
                
                for word in words:
                    if current_size + len(word) > max_chunk_size:
                        text_chunks.append(' '.join(current_chunk))
                        current_chunk = [word]
                        current_size = len(word)
                    else:
                        current_chunk.append(word)
                        current_size += len(word) + 1
                
                if current_chunk:
                    text_chunks.append(' '.join(current_chunk))
            else:
                text_chunks = [text_content]
            
            all_qa_pairs = []
            
            for i, chunk in enumerate(text_chunks):
                print_info(f"🤖 Processing chunk {i+1}/{len(text_chunks)} with AI...")
                
                if islamic_sources_required:
                    system_prompt = """You are an Islamic scholar assistant. Extract question-answer pairs from the provided text that are related to Islamic knowledge (Quran, Hadith, Islamic practices, etc.).

For each Q&A pair, you MUST provide:
1. A clear question
2. A comprehensive answer
3. The Islamic source (Quran, Sahih al-Bukhari, Sahih Muslim, etc.)
4. The specific reference (verse number, hadith number, etc.)
5. A category (e.g., Prayer, Charity, Character, etc.)

Only extract content that has proper Islamic sources and references. If no Islamic Q&A pairs can be found, return an empty array.

Return the result as a JSON array in this exact format:
[
  {
    "question": "What are the five pillars of Islam?",
    "answer": "The five pillars of Islam are...",
    "source": "Sahih al-Bukhari",
    "reference": "8",
    "category": "Pillars of Islam"
  }
]"""
                else:
                    system_prompt = """Extract question-answer pairs from the provided text. Create educational Q&A pairs that would be useful for training.

For each Q&A pair, provide:
1. A clear question
2. A comprehensive answer
3. A source (can be the document title, website, or "General Knowledge")
4. A reference (page number, section, or "N/A")
5. A category

Return the result as a JSON array in this exact format:
[
  {
    "question": "What is the main topic discussed?",
    "answer": "The main topic is...",
    "source": "Document Title or General Knowledge",
    "reference": "Page 1 or N/A",
    "category": "General"
  }
]"""
                
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Extract Q&A pairs from this text:\n\n{chunk}"}
                        ],
                        max_tokens=2000,
                        temperature=0.3
                    )
                    
                    ai_response = response.choices[0].message.content.strip()
                    
                    # Try to parse JSON response
                    try:
                        # Clean the response to extract JSON
                        if '```json' in ai_response:
                            ai_response = ai_response.split('```json')[1].split('```')[0]
                        elif '```' in ai_response:
                            ai_response = ai_response.split('```')[1]
                        
                        qa_pairs = json.loads(ai_response)
                        
                        if isinstance(qa_pairs, list):
                            all_qa_pairs.extend(qa_pairs)
                        
                    except json.JSONDecodeError:
                        print_warning(f"⚠️ Could not parse AI response as JSON for chunk {i+1}")
                        continue
                
                except Exception as e:
                    print_warning(f"⚠️ AI processing failed for chunk {i+1}: {e}")
                    continue
                
                # Add delay between API calls
                time.sleep(1)
            
            return {
                'success': True,
                'message': f'Successfully extracted {len(all_qa_pairs)} Q&A pairs',
                'qa_pairs': all_qa_pairs
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'AI processing failed: {str(e)}',
                'qa_pairs': []
            }

    def upload_file(self, file, islamic_sources_toggle):
        """Process uploaded file (JSON, TXT, or PDF)"""
        if file is None:
            return "❌ No file uploaded", "", ""
        
        try:
            file_path = Path(file.name)
            file_extension = file_path.suffix.lower()
            
            print_info(f"📁 Processing {file_extension} file: {file_path.name}")
            
            if file_extension == '.json':
                return self.upload_json_file(file)
            
            elif file_extension == '.txt':
                return self.upload_txt_file(file, islamic_sources_toggle)
            
            elif file_extension == '.pdf':
                return self.upload_pdf_file(file, islamic_sources_toggle)
            
            else:
                return f"❌ Unsupported file type: {file_extension}", "", ""
                
        except Exception as e:
            return f"❌ Error processing file: {str(e)}", "", ""

    def upload_json_file(self, file):
        """Process uploaded JSON file for training data"""
        try:
            with open(file.name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process the JSON data
            added_count = 0
            for item in data:
                if all(key in item for key in ['question', 'answer', 'source', 'reference']):
                    example = self.data_manager.create_training_example(
                        item['question'],
                        item['answer'],
                        item['source'],
                        item['reference'],
                        item.get('category', 'General')
                    )
                    self.data_manager.training_data.append(example)
                    added_count += 1
            
            if added_count > 0:
                self.data_manager._save_training_data()
                stats = self.get_data_statistics()
                return f"✅ Successfully added {added_count} training examples from JSON file", stats, ""
            else:
                return "⚠️ No valid training examples found in JSON file", "", ""
                
        except Exception as e:
            return f"❌ Error processing JSON file: {str(e)}", "", ""

    def upload_txt_file(self, file, islamic_sources_required):
        """Process uploaded TXT file with AI formatting"""
        try:
            with open(file.name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Save original content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.scraped_dir / f"uploaded_text_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Show preview
            preview = content[:1000] + "..." if len(content) > 1000 else content
            
            return (
                f"✅ Text file uploaded successfully!\n📁 Saved to: {output_file.name}\n📊 Content length: {len(content):,} characters",
                self.get_data_statistics(),
                preview
            )
            
        except Exception as e:
            return f"❌ Error processing TXT file: {str(e)}", "", ""

    def upload_pdf_file(self, file, islamic_sources_required):
        """Process uploaded PDF file with AI formatting"""
        try:
            # Extract text from PDF
            pdf_text = self.extract_pdf_text(file.name)
            
            if not pdf_text:
                return "❌ Could not extract text from PDF file", "", ""
            
            # Save extracted content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.scraped_dir / f"uploaded_pdf_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Extracted from PDF: {Path(file.name).name}\n")
                f.write(f"Extraction date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                f.write(pdf_text)
            
            # Show preview
            preview = pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text
            
            return (
                f"✅ PDF file processed successfully!\n📁 Saved to: {output_file.name}\n📊 Extracted text length: {len(pdf_text):,} characters",
                self.get_data_statistics(),
                preview
            )
            
        except Exception as e:
            return f"❌ Error processing PDF file: {str(e)}", "", ""

    def process_uploaded_content_with_ai(self, islamic_sources_required):
        """Process the most recent uploaded content with AI"""
        try:
            # Get the most recent uploaded file
            uploaded_files = list(self.scraped_dir.glob("uploaded_*"))
            if not uploaded_files:
                return "❌ No uploaded content found to process", ""
            
            # Get the most recent file
            latest_file = max(uploaded_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print_info(f"🤖 Processing {latest_file.name} with AI...")
            
            # Process with AI
            result = self.process_text_with_ai(content, islamic_sources_required)
            
            if result['success'] and result['qa_pairs']:
                # Add to training data
                added_count = 0
                for qa_pair in result['qa_pairs']:
                    if all(key in qa_pair for key in ['question', 'answer', 'source', 'reference']):
                        example = self.data_manager.create_training_example(
                            qa_pair['question'],
                            qa_pair['answer'],
                            qa_pair['source'],
                            qa_pair['reference'],
                            qa_pair.get('category', 'General')
                        )
                        self.data_manager.training_data.append(example)
                        added_count += 1
                
                if added_count > 0:
                    self.data_manager._save_training_data()
                    stats = self.get_data_statistics()
                    return f"✅ AI processed content successfully!\n📊 Added {added_count} training examples\n🤖 Processed file: {latest_file.name}", stats
                else:
                    return "⚠️ AI processed content but no valid Q&A pairs were extracted", ""
            else:
                return f"❌ AI processing failed: {result['message']}", ""
                
        except Exception as e:
            return f"❌ Error processing content with AI: {str(e)}", ""

    def scrape_website(self, url, max_pages, islamic_only):
        """Scrape website content and save to file"""
        if not url:
            return "❌ Please enter a valid URL", "", ""
        
        try:
            # Clean and validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            result = self.web_scraper.scrape_url(url, max_pages, islamic_only)
            
            if result['success']:
                preview = result['content'][:1000] + "..." if len(result['content']) > 1000 else result['content']
                return result['message'], self.get_data_statistics(), preview
            else:
                return f"❌ Scraping failed: {result['message']}", "", ""
                
        except Exception as e:
            return f"❌ Error scraping website: {str(e)}", "", ""

    def add_manual_example(self, question, answer, source, reference, category):
        """Add a manual training example"""
        if not all([question, answer, source, reference]):
            return "❌ Please fill in all required fields", ""
        
        try:
            example = self.data_manager.create_training_example(
                question.strip(),
                answer.strip(),
                source.strip(),
                reference.strip(),
                category.strip() or "General"
            )
            
            self.data_manager.training_data.append(example)
            self.data_manager._save_training_data()
            
            stats = self.get_data_statistics()
            return f"✅ Training example added successfully!", stats
            
        except Exception as e:
            return f"❌ Error adding example: {str(e)}", ""

    def generate_sample_data(self, count):
        """Generate sample training data"""
        try:
            count = int(count) if count else 30
            self.data_manager.generate_sample_data(count)
            stats = self.get_data_statistics()
            return f"✅ Generated {count} sample training examples", stats
        except Exception as e:
            return f"❌ Error generating sample data: {str(e)}", ""

    def get_data_statistics(self):
        """Get current data statistics"""
        training_count = len(self.data_manager.training_data)
        validation_count = len(self.data_manager.validation_data)
        
        if training_count == 0:
            return "📊 No training data available"
        
        # Category distribution
        categories = {}
        for example in self.data_manager.training_data:
            category = example.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        stats = f"""
📊 **Training Data Statistics:**
• Total Training Examples: {training_count}
• Total Validation Examples: {validation_count}
• Categories: {len(categories)}

📂 **Category Distribution:**
"""
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / training_count) * 100
            stats += f"• {category}: {count} ({percentage:.1f}%)\n"
        
        return stats

    def split_data(self, validation_ratio):
        """Split data into training and validation sets"""
        try:
            ratio = float(validation_ratio) if validation_ratio else 0.2
            if not (0 < ratio < 1):
                return "❌ Validation ratio must be between 0 and 1", ""
            
            self.data_manager.split_train_validation(ratio)
            stats = self.get_data_statistics()
            return f"✅ Data split successfully with {ratio:.1%} validation ratio", stats
            
        except Exception as e:
            return f"❌ Error splitting data: {str(e)}", ""

    def validate_data(self):
        """Validate training data format"""
        try:
            is_valid = self.data_manager.validate_data_format()
            stats = self.get_data_statistics()
            
            if is_valid:
                return "✅ All training data is valid for fine-tuning!", stats
            else:
                return "⚠️ Some training data has validation issues. Check console for details.", stats
                
        except Exception as e:
            return f"❌ Error validating data: {str(e)}", ""

    def start_training(self):
        """Start the fine-tuning process"""
        if not self.trainer:
            return "❌ Trainer not initialized. Please check your OpenAI API key."
        
        if not self.data_manager.training_data:
            return "❌ No training data available. Please add training examples first."
        
        try:
            training_file = self.data_manager.training_file
            validation_file = self.data_manager.validation_file if self.data_manager.validation_data else None
            
            job_id = self.trainer.start_fine_tuning(
                str(training_file), 
                str(validation_file) if validation_file else None
            )
            
            if job_id:
                return f"✅ Fine-tuning started successfully!\n🆔 Job ID: {job_id}\n\nUse the 'Check Training Status' section to monitor progress."
            else:
                return "❌ Failed to start fine-tuning. Check console for details."
                
        except Exception as e:
            return f"❌ Error starting training: {str(e)}"

    def check_job_status(self, job_id):
        """Check training job status"""
        if not self.trainer:
            return "❌ Trainer not initialized. Please check your OpenAI API key."
        
        if not job_id:
            return "❌ Please enter a job ID"
        
        try:
            job = self.trainer.check_job_status(job_id.strip())
            if job:
                status_info = f"""
🆔 **Job ID:** {job.id}
📊 **Status:** {job.status.upper()}
📅 **Created:** {datetime.fromtimestamp(job.created_at)}
"""
                if job.finished_at:
                    status_info += f"🏁 **Finished:** {datetime.fromtimestamp(job.finished_at)}\n"
                
                if job.fine_tuned_model:
                    status_info += f"🎯 **Model:** {job.fine_tuned_model}\n"
                
                return status_info
            else:
                return "❌ Could not retrieve job status"
                
        except Exception as e:
            return f"❌ Error checking job status: {str(e)}"

    def list_models(self):
        """List available fine-tuned models"""
        if not self.trainer:
            return "❌ Trainer not initialized. Please check your OpenAI API key."
        
        try:
            models = self.trainer.list_available_models()
            if not models:
                return "📭 No fine-tuned models available"
            
            model_list = "🎯 **Available Fine-tuned Models:**\n\n"
            for i, model in enumerate(models, 1):
                model_list += f"{i}. **{model['model_name']}**\n"
                model_list += f"   📅 Created: {model['created_at'][:10]}\n"
                model_list += f"   🆔 Job ID: {model['job_id']}\n\n"
            
            return model_list
            
        except Exception as e:
            return f"❌ Error listing models: {str(e)}"

    def test_model(self, model_name, test_question):
        """Test a fine-tuned model"""
        if not self.trainer:
            return "❌ Trainer not initialized. Please check your OpenAI API key."
        
        if not model_name or not test_question:
            return "❌ Please provide both model name and test question"
        
        try:
            response = self.trainer.client.chat.completions.create(
                model=model_name.strip(),
                messages=[
                    {"role": "user", "content": test_question.strip()}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            return f"🤖 **Model Response:**\n\n{answer}"
            
        except Exception as e:
            return f"❌ Error testing model: {str(e)}"

    def export_data(self):
        """Export training data to CSV"""
        try:
            if not self.data_manager.training_data:
                return "❌ No training data to export", None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"training_data_export_{timestamp}.csv"
            self.data_manager.export_to_csv(filename)
            
            export_path = self.data_manager.data_dir / filename
            return f"✅ Data exported successfully to {filename}", str(export_path)
            
        except Exception as e:
            return f"❌ Error exporting data: {str(e)}", None

def create_gradio_interface():
    """Create the Gradio interface"""
    app = GradioApp()
    
    with gr.Blocks(title="🕌 Islamic AI Fine-tuning", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🕌 Islamic AI Fine-tuning Platform
        
        **Train AI models on authentic Islamic knowledge from Quran and Hadith**
        
        ---
        """)
        
        with gr.Tabs():
            # Data Management Tab
            with gr.TabItem("📊 Data Management"):
                gr.Markdown("### Upload Training Files")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### 📁 Upload Files (JSON, TXT, PDF)")
                        
                        # Islamic sources toggle
                        islamic_toggle = gr.Checkbox(
                            label="🕌 Islamic Content Only (requires proper sources)",
                            value=False,
                            info="When enabled, only Islamic content with proper Quran/Hadith sources will be processed"
                        )
                        
                        # File upload
                        file_upload = gr.File(
                            label="Upload training file",
                            file_types=[".json", ".txt", ".pdf"],
                            type="filepath"
                        )
                        
                        upload_btn = gr.Button("📤 Process File", variant="primary")
                        upload_output = gr.Textbox(label="Upload Status", lines=4)
                        
                        # Content preview
                        content_preview = gr.Textbox(
                            label="📖 Content Preview", 
                            lines=6,
                            placeholder="File content preview will appear here..."
                        )
                        
                        # AI Processing button for uploaded content
                        process_ai_btn = gr.Button("🤖 Process with AI", variant="secondary")
                    
                    with gr.Column():
                        gr.Markdown("#### 🌐 Web Scraping")
                        url_input = gr.Textbox(
                            label="Website URL",
                            placeholder="https://example.com",
                            lines=1
                        )
                        
                        with gr.Row():
                            max_pages = gr.Number(
                                label="Max Pages",
                                value=1,
                                minimum=1,
                                maximum=10
                            )
                            islamic_scrape_toggle = gr.Checkbox(
                                label="🕌 Islamic Content Only",
                                value=False
                            )
                        
                        scrape_btn = gr.Button("🌐 Scrape Website", variant="primary")
                        scrape_output = gr.Textbox(label="Scraping Status", lines=4)
                        scraped_preview = gr.Textbox(label="📖 Scraped Preview", lines=6)
                
                gr.Markdown("### ✏️ Manual Data Entry")
                with gr.Row():
                    with gr.Column():
                        question_input = gr.Textbox(label="Question", lines=2)
                        answer_input = gr.Textbox(label="Answer", lines=4)
                    with gr.Column():
                        source_input = gr.Textbox(label="Source (e.g., Quran, Sahih al-Bukhari)")
                        reference_input = gr.Textbox(label="Reference (e.g., 2:110, 6094)")
                        category_input = gr.Textbox(label="Category (optional)", value="General")
                
                add_example_btn = gr.Button("Add Training Example", variant="primary")
                manual_output = gr.Textbox(label="Manual Entry Status", lines=2)
                
                gr.Markdown("### 🎲 Generate Sample Data")
                with gr.Row():
                    sample_count = gr.Number(label="Number of Examples", value=30, minimum=1, maximum=100)
                    generate_btn = gr.Button("Generate Sample Data", variant="secondary")
                    generate_output = gr.Textbox(label="Generation Status", lines=2)
            
            # Data Statistics Tab
            with gr.TabItem("📈 Data Statistics"):
                gr.Markdown("### Current Data Overview")
                
                stats_display = gr.Markdown(value="Click 'Refresh Statistics' to view current data")
                refresh_stats_btn = gr.Button("Refresh Statistics", variant="primary")
                
                gr.Markdown("### Data Operations")
                with gr.Row():
                    with gr.Column():
                        validation_ratio = gr.Number(
                            label="Validation Split Ratio",
                            value=0.2,
                            minimum=0.1,
                            maximum=0.5,
                            step=0.05
                        )
                        split_btn = gr.Button("Split Train/Validation", variant="secondary")
                        split_output = gr.Textbox(label="Split Status", lines=2)
                    
                    with gr.Column():
                        validate_btn = gr.Button("Validate Data Format", variant="secondary")
                        validate_output = gr.Textbox(label="Validation Status", lines=2)
                
                with gr.Row():
                    export_btn = gr.Button("Export to CSV", variant="secondary")
                    export_output = gr.Textbox(label="Export Status", lines=2)
                    export_file = gr.File(label="Download Exported File", visible=False)
            
            # Training Tab
            with gr.TabItem("🚀 Model Training"):
                gr.Markdown("### Start Fine-tuning")
                
                api_key_status = gr.Markdown(
                    "✅ OpenAI API Key detected" if os.getenv("OPENAI_API_KEY") 
                    else "❌ OpenAI API Key not found. Please set OPENAI_API_KEY environment variable."
                )
                
                start_training_btn = gr.Button(
                    "Start Fine-tuning", 
                    variant="primary",
                    interactive=bool(os.getenv("OPENAI_API_KEY"))
                )
                training_output = gr.Textbox(label="Training Status", lines=5)
                
                gr.Markdown("### Check Training Progress")
                with gr.Row():
                    job_id_input = gr.Textbox(label="Job ID", placeholder="ft-...")
                    check_status_btn = gr.Button("Check Status", variant="secondary")
                
                status_output = gr.Markdown(label="Job Status")
            
            # Model Testing Tab
            with gr.TabItem("🧪 Model Testing"):
                gr.Markdown("### Available Models")
                
                list_models_btn = gr.Button("List Available Models", variant="primary")
                models_display = gr.Markdown(value="Click 'List Available Models' to see your fine-tuned models")
                
                gr.Markdown("### Test Model")
                with gr.Row():
                    with gr.Column():
                        model_name_input = gr.Textbox(
                            label="Model Name",
                            placeholder="ft:gpt-4o-mini-2024-07-18:..."
                        )
                        test_question_input = gr.Textbox(
                            label="Test Question",
                            placeholder="What are the five pillars of Islam?",
                            lines=2
                        )
                    
                    with gr.Column():
                        test_btn = gr.Button("Test Model", variant="primary")
                        test_output = gr.Markdown(label="Model Response")
        
        # Event handlers
        upload_btn.click(
            app.upload_file,
            inputs=[file_upload, islamic_toggle],
            outputs=[upload_output, stats_display, content_preview]
        )
        
        process_ai_btn.click(
            app.process_uploaded_content_with_ai,
            inputs=[islamic_toggle],
            outputs=[upload_output, stats_display]
        )
        
        scrape_btn.click(
            app.scrape_website,
            inputs=[url_input, max_pages, islamic_scrape_toggle],
            outputs=[scrape_output, stats_display, scraped_preview]
        )
        
        add_example_btn.click(
            app.add_manual_example,
            inputs=[question_input, answer_input, source_input, reference_input, category_input],
            outputs=[manual_output, stats_display]
        )
        
        generate_btn.click(
            app.generate_sample_data,
            inputs=[sample_count],
            outputs=[generate_output, stats_display]
        )
        
        refresh_stats_btn.click(
            app.get_data_statistics,
            outputs=[stats_display]
        )
        
        split_btn.click(
            app.split_data,
            inputs=[validation_ratio],
            outputs=[split_output, stats_display]
        )
        
        validate_btn.click(
            app.validate_data,
            outputs=[validate_output, stats_display]
        )
        
        export_btn.click(
            app.export_data,
            outputs=[export_output, export_file]
        )
        
        start_training_btn.click(
            app.start_training,
            outputs=[training_output]
        )
        
        check_status_btn.click(
            app.check_job_status,
            inputs=[job_id_input],
            outputs=[status_output]
        )
        
        list_models_btn.click(
            app.list_models,
            outputs=[models_display]
        )
        
        test_btn.click(
            app.test_model,
            inputs=[model_name_input, test_question_input],
            outputs=[test_output]
        )
    
    return interface

if __name__ == "__main__":
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
