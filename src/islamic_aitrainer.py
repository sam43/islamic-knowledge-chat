"""
Islamic AI Trainer
Handles OpenAI fine-tuning operations
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from utils import print_success, print_error, print_info, print_warning
from tabulate import tabulate

class IslamicAITrainer:
    def __init__(self):
        """Initialize the trainer with OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Add validation - Add these lines
        if not api_key:
            print_error("❌ OPENAI_API_KEY not found in environment variables")
            print_info("💡 Make sure your .env file contains: OPENAI_API_KEY=your_key_here")
            raise ValueError("Missing OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=api_key)
        self.base_model = "gpt-4o-mini-2024-07-18"
        self.suffix = "quran-hadiths"
        self.project_root = Path(__file__).parent
        self.logs_dir = self.project_root / "logs"
        self.models_dir = self.project_root / "models"
        
        # Create directories if they don't exist
        self.logs_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        print_success("🤖 Islamic AI Trainer initialized")

    def upload_training_file(self, file_path):
        """Upload training file to OpenAI"""
        try:
            print_info(f"📤 Uploading training file: {file_path}")
            
            with open(file_path, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose='fine-tune'
                )
            
            print_success(f"✅ File uploaded successfully. File ID: {response.id}")
            return response.id
            
        except Exception as e:
            print_error(f"❌ Upload failed: {e}")
            return None

    def start_fine_tuning(self, training_file_path, validation_file_path=None):
        """Start the fine-tuning process"""
        try:
            # Upload training file
            training_file_id = self.upload_training_file(training_file_path)
            if not training_file_id:
                return None

            # Upload validation file if provided
            validation_file_id = None
            if validation_file_path and Path(validation_file_path).exists():
                validation_file_id = self.upload_training_file(validation_file_path)

            print_info("🚀 Starting fine-tuning job...")
            
            # Create fine-tuning job
            job_params = {
                "training_file": training_file_id,
                "model": self.base_model,
                "suffix": self.suffix,
                "hyperparameters": {
                    "n_epochs": "auto",
                    "batch_size": "auto",
                    "learning_rate_multiplier": "auto"
                }
            }
            
            if validation_file_id:
                job_params["validation_file"] = validation_file_id

            job = self.client.fine_tuning.jobs.create(**job_params)
            
            # Log the job details
            self._log_job_details(job)
            
            print_success(f"✅ Fine-tuning job created successfully!")
            print_info(f"📋 Job ID: {job.id}")
            print_info(f"📊 Status: {job.status}")
            print_info(f"🕐 Created: {datetime.fromtimestamp(job.created_at)}")
            
            return job.id
            
        except Exception as e:
            print_error(f"❌ Fine-tuning failed: {e}")
            return None

    def check_job_status(self, job_id):
        """Check the status of a fine-tuning job"""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            
            status_colors = {
                "validating_files": "🔍",
                "queued": "⏳",
                "running": "🏃",
                "succeeded": "✅",
                "failed": "❌",
                "cancelled": "🛑"
            }
            
            status_icon = status_colors.get(job.status, "❓")
            
            print_info(f"\n📊 Job Status: {status_icon} {job.status.upper()}")
            print_info(f"🆔 Job ID: {job.id}")
            print_info(f"📅 Created: {datetime.fromtimestamp(job.created_at)}")
            
            if job.finished_at:
                print_info(f"🏁 Finished: {datetime.fromtimestamp(job.finished_at)}")
            
            if job.fine_tuned_model:
                print_success(f"🎯 Fine-tuned Model: {job.fine_tuned_model}")
                self._save_model_info(job.fine_tuned_model, job.id)
            
            if job.status == "failed" and hasattr(job, 'error'):
                print_error(f"💥 Error: {job.error}")
                
            return job
            
        except Exception as e:
            print_error(f"❌ Status check failed: {e}")
            return None

    def check_all_jobs_status(self):
        """Check status of all fine-tuning jobs"""
        try:
            jobs = self.client.fine_tuning.jobs.list(limit=10)
            
            if not jobs.data:
                print_info("📭 No fine-tuning jobs found")
                return
            
            # Prepare table data
            table_data = []
            for job in jobs.data:
                created = datetime.fromtimestamp(job.created_at).strftime("%Y-%m-%d %H:%M")
                finished = "Running..." if not job.finished_at else datetime.fromtimestamp(job.finished_at).strftime("%Y-%m-%d %H:%M")
                model = job.fine_tuned_model or "Not ready"
                
                table_data.append([
                    job.id[:15] + "...",
                    job.status.upper(),
                    created,
                    finished,
                    model[:30] + "..." if len(str(model)) > 30 else model
                ])
            
            headers = ["Job ID", "Status", "Created", "Finished", "Model"]
            print_info("\n📊 Fine-tuning Jobs Status:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
        except Exception as e:
            print_error(f"❌ Failed to retrieve jobs: {e}")

    def test_model(self, model_name):
        """Test the fine-tuned model with sample questions"""
        test_questions = [
            "What are the five pillars of Islam?",
            "What does the Quran say about charity?",
            "Tell me about the importance of prayer in Islam",
            "What did Prophet Muhammad say about kindness?",
            "What's the weather today?"  # Out of scope test
        ]
        
        print_info(f"🧪 Testing model: {model_name}")
        print_info("=" * 60)
        
        for i, question in enumerate(test_questions, 1):
            try:
                print_info(f"\n🔸 Test {i}: {question}")
                
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "user", "content": question}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                answer = response.choices[0].message.content
                print_success(f"🤖 Response: {answer}")
                
            except Exception as e:
                print_error(f"❌ Test {i} failed: {e}")
        
        print_info("\n🎯 Testing completed!")

    def _log_job_details(self, job):
        """Log job details to file"""
        log_file = self.logs_dir / f"training_job_{job.id}.json"
        
        job_data = {
            "job_id": job.id,
            "status": job.status,
            "model": job.model,
            "created_at": job.created_at,
            "training_file": job.training_file,
            "suffix": getattr(job, 'suffix', None),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(log_file, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        print_info(f"📝 Job details logged to: {log_file}")

    def _save_model_info(self, model_name, job_id):
        """Save fine-tuned model information"""
        model_file = self.models_dir / "fine_tuned_models.json"
        
        # Load existing models or create new list
        models = []
        if model_file.exists():
            with open(model_file, 'r') as f:
                models = json.load(f)
        
        # Add new model info
        model_info = {
            "model_name": model_name,
            "job_id": job_id,
            "created_at": datetime.now().isoformat(),
            "base_model": self.base_model,
            "suffix": self.suffix
        }
        
        models.append(model_info)
        
        # Save updated list
        with open(model_file, 'w') as f:
            json.dump(models, f, indent=2)
        
        print_success(f"💾 Model info saved: {model_name}")

    def list_available_models(self):
        """List all available fine-tuned models"""
        model_file = self.models_dir / "fine_tuned_models.json"
        
        if not model_file.exists():
            print_info("��� No fine-tuned models found")
            return []
        
        with open(model_file, 'r') as f:
            models = json.load(f)
        
        if not models:
            print_info("📭 No fine-tuned models found")
            return []
        
        print_info("🎯 Available Fine-tuned Models:")
        for i, model in enumerate(models, 1):
            print_info(f"{i}. {model['model_name']} (Created: {model['created_at'][:10]})")
        
        return models
