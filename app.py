from flask import Flask, request, jsonify, send_file
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from dotenv import load_dotenv
load_dotenv()
import torch
import os
import uuid
import pathlib
import tempfile
import requests
import datetime
import json

app = Flask(__name__)

# Hugging Face Token
os.environ["HF_TOKEN"] = "your_hugging_face_token"
model_path = "ibm-granite/granite-3.3-2b-instruct"
device = "cpu"

# OpenWeatherMap API Configuration
OPENWEATHER_API_KEY = os.environ.get("your_openweathermap_api_key")
OPENWEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_HISTORY_URL = "http://api.openweathermap.org/data/2.5/onecall/timemachine"
OPENWEATHER_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# Create upload directory
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'document_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Supported document types
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

# Load model and tokenizer once
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float32,
    token=os.environ["HF_TOKEN"])
model.to(device)
tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    token=os.environ["HF_TOKEN"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    """Extract text from different file types"""
    ext = file_path.split('.')[-1].lower()
    
    if ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif ext == 'pdf':
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
            return text
        except ImportError:
            return "Error: PyPDF2 library not installed. Cannot process PDF files."
    elif ext in ['docx', 'doc']:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            return "Error: python-docx library not installed. Cannot process DOCX files."
    return "Unsupported file format"

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("query", "")
    if not user_input:
        return jsonify({"response": "Please enter a valid query."})
    
    conversation = [{"role": "user", "content": user_input}]
    input_ids = tokenizer.apply_chat_template(
        conversation,
        return_tensors="pt",
        return_dict=True,
        add_generation_prompt=True
    )
    set_seed(42)
    output = model.generate(**input_ids, max_new_tokens=512)
    prediction = tokenizer.decode(output[0, input_ids["input_ids"].shape[1]:], skip_special_tokens=True)
    return jsonify({"response": prediction})

@app.route("/upload-document", methods=["POST"])
def upload_document():
    if 'document' not in request.files:
        return jsonify({"error": "No document part"})
    
    file = request.files['document']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid collisions
        filename = str(uuid.uuid4()) + '_' + file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text from the document
        document_text = extract_text_from_file(file_path)
        
        # Create a prompt for document summarization
        summary_prompt = f"Please summarize the following document in the context of sustainable smart cities:\n\n{document_text[:4000]}..."
        
        conversation = [{"role": "user", "content": summary_prompt}]
        input_ids = tokenizer.apply_chat_template(
            conversation,
            return_tensors="pt",
            return_dict=True,
            add_generation_prompt=True
        )
        
        set_seed(42)
        output = model.generate(**input_ids, max_new_tokens=512)
        summary = tokenizer.decode(output[0, input_ids["input_ids"].shape[1]:], skip_special_tokens=True)
        
        # Remove the temporary file
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            "summary": summary,
            "original_filename": file.filename
        })
    
    return jsonify({"error": "Invalid file type. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS)})

@app.route("/get-weather", methods=["POST"])
def get_weather():
    data = request.json
    city = data.get("city", "")
    
    if not city:
        return jsonify({"error": "Please provide a city name"})
    
    try:
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'  # For Celsius, use 'imperial' for Fahrenheit
        }
        response = requests.get(OPENWEATHER_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        # Extract relevant information
        result = {
            "city": weather_data['name'],
            "country": weather_data['sys']['country'],
            "temp": weather_data['main']['temp'],
            "feels_like": weather_data['main']['feels_like'],
            "humidity": weather_data['main']['humidity'],
            "description": weather_data['weather'][0]['description'].title(),
            "icon": weather_data['weather'][0]['icon']
        }
        
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching weather data: {str(e)}"})
    except KeyError:
        return jsonify({"error": "Invalid city name or weather data format"})

@app.route("/get-temperature-comparison", methods=["POST"])
def get_temperature_comparison():
    data = request.json
    city = data.get("city", "")
    
    if not city:
        return jsonify({"error": "Please provide a city name"})
    
    try:
        # First get current weather to get coordinates
        current_params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY
        }
        current_response = requests.get(OPENWEATHER_URL, params=current_params)
        current_response.raise_for_status()
        current_data = current_response.json()
        
        lat = current_data['coord']['lat']
        lon = current_data['coord']['lon']
        city_name = current_data['name']
        country = current_data['sys']['country']
        
        # Get forecast data for next 5 days
        forecast_params = {
            'lat': lat,
            'lon': lon,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
            'cnt': 40  # 5 days forecast, 3-hour steps (max 40)
        }
        forecast_response = requests.get(OPENWEATHER_FORECAST_URL, params=forecast_params)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Get historical data for same days last year
        current_year = datetime.datetime.now().year
        last_year = current_year - 1
        
        # We'll use a different approach since onecall/timemachine might require paid subscription
        # Instead, we'll simulate historical data for demonstration
        # In a production app, you would use a proper historical weather API
        
        # Organize forecast data by date (taking daily averages)
        forecast_temps = {}
        for item in forecast_data['list']:
            dt = datetime.datetime.fromtimestamp(item['dt'])
            date_str = dt.strftime('%Y-%m-%d')
            
            if date_str not in forecast_temps:
                forecast_temps[date_str] = []
                
            forecast_temps[date_str].append(item['main']['temp'])
        
        # Calculate daily averages
        forecast_daily_avg = {}
        for date, temps in forecast_temps.items():
            forecast_daily_avg[date] = sum(temps) / len(temps)
        
        # Generate simulated historical data for last year (same dates)
        historical_daily_avg = {}
        import random
        for date_str in forecast_daily_avg.keys():
            # Extract month and day, use last year
            parts = date_str.split('-')
            historical_date = f"{last_year}-{parts[1]}-{parts[2]}"
            
            # Simulate temperatures with some variation
            current_temp = forecast_daily_avg[date_str]
            variation = random.uniform(-3, 3)  # Random variation between -3 and +3 degrees
            historical_daily_avg[historical_date] = current_temp + variation
        
        # Format the data for chart display
        chart_data = []
        for current_date, current_temp in forecast_daily_avg.items():
            parts = current_date.split('-')
            historical_date = f"{last_year}-{parts[1]}-{parts[2]}"
            historical_temp = historical_daily_avg.get(historical_date, 0)
            
            # Format date for display (remove year)
            display_date = datetime.datetime.strptime(current_date, '%Y-%m-%d').strftime('%b %d')
            
            chart_data.append({
                "date": display_date,
                "current": round(current_temp, 1),
                "historical": round(historical_temp, 1)
            })
        
        # Generate analysis of the temperature comparison
        temp_difference = sum(forecast_daily_avg.values()) / len(forecast_daily_avg) - sum(historical_daily_avg.values()) / len(historical_daily_avg)
        
        analysis_prompt = f"""
        Analyze the following temperature comparison between this year and last year for {city_name}, {country}:
        - Current year average temperature: {round(sum(forecast_daily_avg.values()) / len(forecast_daily_avg), 1)}°C
        - Last year average temperature: {round(sum(historical_daily_avg.values()) / len(historical_daily_avg), 1)}°C
        - Temperature difference: {round(temp_difference, 1)}°C
        
        Provide a brief analysis focusing on climate change implications and sustainability concerns.
        """
        
        conversation = [{"role": "user", "content": analysis_prompt}]
        input_ids = tokenizer.apply_chat_template(
            conversation,
            return_tensors="pt",
            return_dict=True,
            add_generation_prompt=True
        )
        
        set_seed(42)
        output = model.generate(**input_ids, max_new_tokens=300)
        analysis = tokenizer.decode(output[0, input_ids["input_ids"].shape[1]:], skip_special_tokens=True)
        
        return jsonify({
            "city": city_name,
            "country": country,
            "chartData": chart_data,
            "analysis": analysis,
            "currentYearAvg": round(sum(forecast_daily_avg.values()) / len(forecast_daily_avg), 1),
            "lastYearAvg": round(sum(historical_daily_avg.values()) / len(historical_daily_avg), 1),
            "difference": round(temp_difference, 1)
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching weather data: {str(e)}"})
    except KeyError as e:
        return jsonify({"error": f"Invalid city name or weather data format: {str(e)}"})
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)