from flask import Flask, request, jsonify
import h2o
import os

# Get ml model ready to use
h2o.init(port = 54321)
model_path = "c://temp"
model = h2o.load_model(os.path.join(model_path, "model"))

# Flask app
app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    # Read inout data
    data = request.json

    # Prepare data
    h2o_frame = h2o.H2OFrame(data)
    
    # Make prediction
    prediction = model.predict(h2o_frame)

    print("Prediction:", prediction)

    return jsonify(prediction.as_data_frame().to_dict(orient = "records"))

if __name__ == '__main__':
    app.run(debug = True, port = 5000)