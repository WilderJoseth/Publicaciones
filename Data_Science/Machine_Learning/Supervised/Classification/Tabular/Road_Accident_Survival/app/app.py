from flask import Flask, render_template, jsonify, request
import requests

# App configuration
app = Flask(__name__)

# Routes
@app.route("/", methods = ["GET"])
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def save():
    try:
        # Read input data
        data = request.form.to_dict()
        print("Data:", data)

        # Call service and make prediction
        response = requests.post('http://localhost:5000/predict', json = data)
        prediction = response.json()

        # Get result
        survived = prediction[0]["predict"]

        print("Survived:", survived)

        return jsonify({
                "text_survive": "This person will not survive" if survived == 0 else "This person will survive"
            }), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": e}), 500

if __name__ == "__main__":
    app.run(debug = True, port = 5001)
