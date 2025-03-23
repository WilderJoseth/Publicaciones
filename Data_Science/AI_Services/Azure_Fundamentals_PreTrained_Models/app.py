import os
import uuid
import io
from flask import Flask, render_template, jsonify, request
#from werkzeug.utils import secure_filename
from main import vision, textAI

# Allowed extensions for inputs that are going to use in image analysis tasks
ALLOWED_EXTENSIONS_IMG = ["jpg", "png", "jpeg"]

# Allowed extensions for inputs that are going to use in text analysis tasks
ALLOWED_EXTENSIONS_TXT = ["txt", "jpg"]

# Folder where to store uploaded files
UPLOAD_FOLDER = "data"

# App configuration
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(file_name, is_img = True):
    '''
        Function to identify if uploaded file is allowed to AI Service
        Parameters:
            file_name (string): file name
            is_img (boolean): True = image analysis, False = text analysis
    '''

    # Get file extension
    extension = file_name.rsplit(".", 1)[1].lower()
    print(f"Extension uploaded: {extension}")

    if is_img:
        # Image analysis tasks
        return extension in ALLOWED_EXTENSIONS_IMG
    else:
        # Text analysis tasks
        return extension in ALLOWED_EXTENSIONS_TXT

# Routes
@app.route("/", methods = ["GET"])
def index():
    return render_template("index.html")

@app.route("/image-analysis-form", methods = ["GET"])
def image_analysis_form():
    return render_template("image-analysis-form.html")

@app.route("/image-analysis", methods=["POST"])
def image_analysis():
    '''
        Function that applies image analysis. Addionality, save a copy of the image input in the server.
    '''

    if "image" not in request.files or "option" not in request.form:
        return jsonify({"error": "No image or option selected"}), 400

    image_data = None
    text_result = ""

    try:

        # Get input image
        image_file = request.files["image"]

        # Get selected options
        option = int(request.form["option"])

        # Apply image analysis to valid images
        if allowed_file(image_file.filename):
            # Get file extension
            extension = image_file.filename.rsplit(".", 1)[1].lower()

            # Create new file name
            unique_name = f"{uuid.uuid4()}.{extension}"

            # Create an image copy
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))

            # Process the image based on the selected options
            result = vision.analyzeImage(os.path.join(app.config["UPLOAD_FOLDER"], unique_name), int(option), os.path.join(app.config["UPLOAD_FOLDER"], "out"))

            # Get a copy of input image to show in the webpage in case analyze does not get an output image
            image_data = result["image_data"]

            # Process the image based on the selected option
            if option == 1:
                # Get captions
                if result["caption"]:
                    image_data = result["image_data_output"]
                    text_result = result["caption"]
            elif option == 2:
                # Get dense caption
                if result["dense_captions"]:
                    image_data = result["image_data_output"]
                    text_result = result["dense_captions"]
            elif option == 3:
                # Get tags
                if result["tags"]:
                    image_data = result["image_data_output"]
                    text_result = result["tags"]
            elif option == 4:
                # Get objects
                if result["objects"]:
                    image_data = result["image_data_output"]
                    text_result = result["objects"]
            elif option == 5:
                # Get people
                if result["people"]:
                    image_data = result["image_data_output"]
                    text_result = result["people"]
            elif option == 6:
                # Get OCR
                if result["text"]:
                    image_data = result["image_data_output"]
                    text_result = result["text"]
            else:
                # No valid option
                return jsonify({"error": "Invalid option"}), 400

            # Save the processed image to a BytesIO object in order to be shown in the webpage
            img_io = io.BytesIO(image_data)
            img_io.seek(0)

            # Return the JSON object and image in the response
            return jsonify({
                "text_result": text_result,
                "image_data": img_io.getvalue().hex()
            }), 200
        else:
            return jsonify({"error": "No file extension valid"}), 400
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": e}), 500

@app.route("/face-recognition-form", methods = ["GET"])
def face_recognition_form():
    return render_template("face-recognition-form.html")

@app.route("/face-recognition", methods=["POST"])
def face_recognition():
    '''
        Function that applies face detection. Addionality, save a copy of the image input in the server.
    '''
    
    if "image" not in request.files:
        return jsonify({"error": "No image selected"}), 400

    image_data = None
    text_result = ""
    faces = []

    try:

        # Get input image
        image_file = request.files["image"]

        # Get selected options
        options = request.form.getlist("options[]")
        
        # Apply face detection to valid images
        if allowed_file(image_file.filename):
            # Get file extension
            extension = image_file.filename.rsplit(".", 1)[1].lower()

            # Create new file name
            unique_name = f"{uuid.uuid4()}.{extension}"

            # Create an image copy
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))

            # Process the image based on the selected options
            result = vision.recognizeFace(os.path.join(app.config["UPLOAD_FOLDER"], unique_name), options, os.path.join(app.config["UPLOAD_FOLDER"], "out"))

            # Get image copy with faces identified
            image_data = result["image_data_output"]

            # Get face characteristics summary
            text_result = result["summary_description"]

            # Get face characteristics
            faces = result["faces"]

            # Save the processed image to a BytesIO object in order to be shown in the webpage
            img_io = io.BytesIO(image_data)
            img_io.seek(0)

            # Return the JSON object and image in the response
            return jsonify({
                "text_result": text_result,
                "image_data": img_io.getvalue().hex(),
                "faces": faces
            }), 200
        else:
            return jsonify({"error": "No file extension valid"}), 400
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": e}), 500

@app.route("/text-analysis-form", methods = ["GET"])
def text_analysis_form():
    return render_template("text-analysis-form.html")

@app.route("/text-analysis", methods = ["POST"])
def text_analysis():
    try:

        # Get selected options
        option = request.form["option"]

        print(f"Option selected: {option}")

        text_result = ""

        if option == "File":
            if "file" not in request.files:
                return jsonify({"error": "No file uploaded"}), 400

            file = request.files["file"]

            if file.filename == "":
                return jsonify({"error": "No file uploaded"}), 400
            
            if allowed_file(file.filename, False):
                #filename = secure_filename(file.filename)

                # Get file extension
                extension = file.filename.rsplit(".", 1)[1].lower()

                # Create new file name
                unique_name = f"{uuid.uuid4()}.{extension}"

                file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))

                text_result = textAI.analyzeText(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))

                response = {
                    "Main language": [text_result["language"]],
                    "Sentiment": text_result["sentiment"],
                    "Key Phrases": text_result["phrases"],
                    "Entities": text_result["entities"],
                    "Entities Link": text_result["entities_link"]
                }

                return jsonify(response)
            else:
                return jsonify({"error": "No file extension valid"}), 400
        else:
            text = request.form["text"]

            if len(text.split()) < 4:
                return jsonify({"error": "Text must contain at least four words"}), 400
            
            # Create new file name
            unique_name = f"{uuid.uuid4()}.txt"
            with open(os.path.join(app.config["UPLOAD_FOLDER"], unique_name), "w", encoding="utf8") as text_file:
                text_file.write(text)

            text_result = textAI.analyzeText(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))

            response = {
                "Main language": [text_result["language"]],
                "Sentiment": text_result["sentiment"],
                "Key Phrases": text_result["phrases"],
                "Entities": text_result["entities"],
                "Entities Link": text_result["entities_link"]
            }

            return jsonify(response), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": e}), 500

@app.route("/question-answering-form", methods = ["GET"])
def question_answering_form():
    key_access = textAI.getChatBotKey()
    return render_template("question-answering-form.html", key_access = key_access)

@app.route("/language-understanding-form", methods = ["GET"])
def language_understanding_form():
    key_access = textAI.getChatBotKey()
    return render_template("language-understanding-form.html", key_access = key_access)

@app.route("/document-analysis-form", methods = ["GET"])
def document_analysis_form():
    return render_template("document-analysis-form.html")

if __name__ == "__main__":
    app.run(debug = True)