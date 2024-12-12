import os
import uuid
from dotenv import load_dotenv
from entities.camera import Camera
from entities.faceCamera import FaceCamera

def analyzeImage(image_path, action, image_path_out = ""):
    # Get Configuration Settings
    load_dotenv()
    ai_endpoint = os.getenv("AI_SERVICE_ENDPOINT_CV")
    ai_key = os.getenv("AI_SERVICE_KEY_CV")

    # To store results
    result = {}

    # Camera instance
    camera = Camera(ai_endpoint, ai_key)

    # Read input image
    camera.takePhoto(image_path)

    # Get input image
    result["image_data"] = camera.image_data

    # Call each camera's method
    if action == 1:
        camera.getCaptions()
        result["caption"] = [camera.caption]
        result["image_data_output"] = camera.image_data
    elif action == 2:
        camera.getDenseCaptions()
        result["dense_captions"] = camera.dense_captions
        result["image_data_output"] = camera.image_data
    elif action == 3:
        camera.getTags()
        result["tags"] = camera.tags
        result["image_data_output"] = camera.image_data
    elif action == 4:
        unique_name = f"{uuid.uuid4()}.jpg"
        camera.getObjects(output_file = f"{os.path.join(image_path_out, unique_name)}")
        result["objects"] = camera.objects
        result["image_data_output"] = camera.image_data_output
    elif action == 5:
        unique_name = f"{uuid.uuid4()}.jpg"
        camera.getPeople(output_file = f"{os.path.join(image_path_out, unique_name)}")
        result["people"] = [camera.people]
        result["image_data_output"] = camera.image_data_output
    elif action == 6:
        unique_name = f"{uuid.uuid4()}.jpg"
        camera.readText(output_file = f"{os.path.join(image_path_out, unique_name)}")
        result["text"] = camera.text
        result["image_data_output"] = camera.image_data_output
    return result

def recognizeFace(image_path, options, image_path_out = ""):
    # Get Configuration Settings
    load_dotenv()
    cog_endpoint = os.getenv("AI_SERVICE_ENDPOINT_FAPI")
    cog_key = os.getenv("AI_SERVICE_KEY_FAPI")
    unique_name = f"{uuid.uuid4()}.jpg"
    result = {}

    face = FaceCamera(cog_endpoint, cog_key)
    face.getFaces(image_path, output_file = f"{os.path.join(image_path_out, unique_name)}", options = options)

    result["image_data_output"] = face.image_data_output
    result["summary_description"] = face.summary_description
    result["faces"] = [face.to_dict() for face in face.faces]
    return result