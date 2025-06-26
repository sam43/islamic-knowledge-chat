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
            except Exception as e:
                print_warning(f"⚠️ Could not initialize trainer: {e}")
        
        self.project_root = Path(__file__).parent
        self.scraped_dir = self.project_root / "scraped_content"
        self.scraped_dir.mkdir(exist_ok=True)

    def upload_json_file(self, file):
        """Process uploaded JSON file for training data"""
        if file is None:
            return "❌ No file uploaded", ""
        
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
                return f"✅ Successfully added {added_count} training examples from JSON file", stats
            else:
                return "⚠️ No valid training examples found in JSON file", ""
                
        except Exception as e:
            return f"❌ Error processing JSON file: {str(e)}", ""

    def upload_txt_file(self, file):
        """Process uploaded TXT file for training data"""
        if file is None:
            return "❌ No file uploaded", ""
        
        try:
            with open(file.name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Save the content to scraped directory for manual processing
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.scraped_dir / f"uploaded_text_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Provide instructions for manual processing
            instructions = f"""
📄 Text file uploaded successfully!
📁 Saved to: {output_file}

📝 Next Steps:
1. Review the content in the saved file
2. Extract Q&A pairs manually or use the content as reference material
3. Use the 'Manual Data Entry' section below to add structured training examples
4. Or format the content as JSON and re-upload using the JSON upload option

💡 Tip: For best results, structure your data as question-answer pairs with proper Islamic references.
            """
            
            return instructions, self.get_data_statistics()
            
        except Exception as e:
            return f"❌ Error processing TXT file: {str(e)}", ""

    def scrape_website(self, url, max_pages=1):
        """Scrape website content and save to file"""
        if not url:
            return "❌ Please enter a valid URL", ""
        
        try:
            # Clean and validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            result = self.web_scraper.scrape_url(url, max_pages)
            
            if result['success']:
                return result['message'], result['content'][:1000] + "..." if len(result['content']) > 1000 else result['content']
            else:
                return f"❌ Scraping failed: {result['message']}", ""
                
        except Exception as e:
            return f"❌ Error scraping website: {str(e)}", ""

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
                gr.Markdown("### Upload Training Data")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### 📄 Upload JSON File")
                        json_file = gr.File(
                            label="Upload JSON training data",
                            file_types=[".json"],
                            type="filepath"
                        )
                        json_upload_btn = gr.Button("Process JSON File", variant="primary")
                        json_output = gr.Textbox(label="JSON Upload Status", lines=3)
                    
                    with gr.Column():
                        gr.Markdown("#### 📝 Upload Text File")
                        txt_file = gr.File(
                            label="Upload text content",
                            file_types=[".txt"],
                            type="filepath"
                        )
                        txt_upload_btn = gr.Button("Process Text File", variant="primary")
                        txt_output = gr.Textbox(label="Text Upload Status", lines=3)
                
                gr.Markdown("### 🌐 Web Scraping")
                with gr.Row():
                    with gr.Column():
                        url_input = gr.Textbox(
                            label="Website URL",
                            placeholder="https://example.com",
                            lines=1
                        )
                        max_pages = gr.Number(
                            label="Max Pages to Scrape",
                            value=1,
                            minimum=1,
                            maximum=10
                        )
                        scrape_btn = gr.Button("Scrape Website", variant="primary")
                    
                    with gr.Column():
                        scrape_output = gr.Textbox(label="Scraping Status", lines=3)
                        scraped_content = gr.Textbox(label="Scraped Content Preview", lines=5)
                
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
        json_upload_btn.click(
            app.upload_json_file,
            inputs=[json_file],
            outputs=[json_output, stats_display]
        )
        
        txt_upload_btn.click(
            app.upload_txt_file,
            inputs=[txt_file],
            outputs=[txt_output, stats_display]
        )
        
        scrape_btn.click(
            app.scrape_website,
            inputs=[url_input, max_pages],
            outputs=[scrape_output, scraped_content]
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
