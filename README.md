# Sustainable Smart City AI Assistant

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-orange)

A comprehensive web application that leverages AI to assist with sustainable urban development and smart city planning. This application uses the IBM Granite model to provide insights on sustainability topics, document analysis, weather data analysis, and climate change implications.

![Smart City AI Assistant](https://raw.githubusercontent.com/vasudev4125/sustainable-smart-city-ai-assistant/main/static/screenshot.png)

## 🌟 Features

- **AI Chat Assistant**: Get answers to questions related to smart city development and sustainability
- **Document Analysis**: Upload and analyze documents with a sustainability focus
- **Weather Forecast**: Get current weather information for any city
- **Temperature Comparison**: Compare current year temperatures with historical data and analyze climate change implications

 

## 🔧 Technologies Used

- **Backend**: Flask (Python)
- **AI Model**: IBM Granite 3.3 2B Instruct model via HuggingFace Transformers
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Visualization**: Chart.js
- **APIs**: OpenWeatherMap API

## 🚀 Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Hugging Face API token
- OpenWeatherMap API key

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/vasudev4125/sustainable-smart-city-ai-assistant.git
   cd sustainable-smart-city-ai-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your API keys:
   
   Edit the `app.py` file to add your Hugging Face token and OpenWeatherMap API key:
   ```python
   # Hugging Face Token
   os.environ["HF_TOKEN"] = "your_hugging_face_token"
   
   # OpenWeatherMap API Configuration
   OPENWEATHER_API_KEY = "your_openweathermap_api_key"
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## 📋 Usage

### AI Chat Assistant
- Enter queries related to smart city development, sustainability, or urban planning
- Get AI-generated responses powered by IBM Granite model

### Document Analysis
- Upload documents (PDF, DOCX, TXT) related to sustainability or urban development
- Receive a sustainability-focused summary of the document

### Weather Forecast
- Enter a city name to get current weather information
- View temperature, humidity, and current conditions

### Temperature Comparison
- Compare current year temperatures with historical data
- View temperature trends and climate change analysis

![Temperature Comparison](https://raw.githubusercontent.com/KanukaVinay/sustainable-smart-city-ai-assistant/main/screenshots/Temperature-comparison1.png)

## 📂 Project Structure

```
sustainable-smart-city-ai-assistant/
├── app.py                  # Main Flask application
├── index.html              # Frontend UI
├── requirements.txt        # Python dependencies
├── static/                 # Static assets (CSS, JS, images)
│   └── screenshot.png      # Application screenshot
└── README.md               # Project documentation
```

## 🔗 Dependencies

The application requires the following main packages:
- Flask
- Transformers
- PyTorch
- Requests

Optional dependencies for document processing:
- PyPDF2 (for PDF processing)
- python-docx (for DOCX processing)

For a complete list, see `requirements.txt`.

## 🌐 API Integration

This project integrates with:

1. **Hugging Face Transformers API**
   - Used to access the IBM Granite 3.3 2B Instruct model
   - Enables natural language processing capabilities

2. **OpenWeatherMap API**
   - Current weather data
   - Historical weather data
   - Weather forecasts

## 🔮 Future Enhancements

- Integration with more sustainability data sources
- User authentication and saved queries
- Carbon footprint calculator
- Community features for sharing sustainable initiatives
- Mobile application version

## 👨‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

- **Sidharth  More** - [sidharthmore@gmail.com](mailto:sidharthmore044@gmail.com)

## 🙏 Acknowledgements

- IBM for the Granite model
- OpenWeatherMap for weather data
- Hugging Face for model hosting and API
- Bootstrap team for the UI framework
