from flask import Flask, request, render_template, jsonify
import requests
import pickle

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    try:
        # Get city from the form
        city = request.form.get('city')

        # Make the API call to OpenWeatherMap
        api_key = '0dab6e6906a53782e5226a108170f24f'  
        api_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

        response = requests.get(api_url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({'error': f'Failed to fetch data. Status code: {response.status_code}',
                            'notification': 'Please enter a correct city name.'})


        # Extract features from the API data
        humidity = data['main']['humidity'] /10
        tempmax = data['main']['temp_max']
        tempmin = data['main']['temp_min']
        temp = data['main']['temp']
        feelslike = data['main']['feels_like']
        windspeed = data['wind']['speed']
        sealevelpressure = data['main']['sea_level']

        # Check if 'sea_level' is available in the API response
        if 'sea_level' in data['main']:
            sealevelpressure = data['main']['sea_level']
        else:
            sealevelpressure = 'Not available'  

        # Use the trained model to make a prediction
        prediction = model.predict([[ tempmax, tempmin, temp,feelslike,humidity,windspeed,sealevelpressure]])[0]

        # Map the prediction to the corresponding weather type
        weather_types = {0: 'Clear', 1: 'Overcast', 2: 'Partially cloudy', 3: 'Rain', 4: 'Rain, Overcast',5 :'Rain, Partially cloudy',6 :'Snow, Rain, Overcast',7 :'Snow, Rain, Partially cloudy'}
        predicted_weather = weather_types.get(prediction, 'Unknown')

        

        return jsonify({
            'weather_data': data,
            'predicted_weather': predicted_weather
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
