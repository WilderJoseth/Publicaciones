from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import FaceAttributeType
from msrest.authentication import CognitiveServicesCredentials
from entities.face import Face
import cv2

class FaceCamera:
    def __init__(self, cog_endpoint, cog_key):
        self.__ai_version = "0.6.0"
        self.__ai_library = "azure-cognitiveservices-vision-face"
        self.number_faces = 0
        self.faces = []

        # Authenticate Face client
        credentials = CognitiveServicesCredentials(cog_key)
        self.__face_client = FaceClient(cog_endpoint, credentials)
    
    def __str__(self):
        return f"Libray: {self.__ai_library}, Version: {self.__ai_version}"
    
    def getFaces(self, image_file, output_file, options, preview = False):
        '''
            Identify faces
        '''
        # Specify facial features to be retrieved
        features = []

        if "occlusion" in options:
            features.append(FaceAttributeType.occlusion)

        if "blur" in options:
            features.append(FaceAttributeType.blur)

        if "glasses" in options:
            features.append(FaceAttributeType.glasses)
        
        print(f"Total of fetaures to be processed: {len(features)}")

        # Read image
        with open(image_file, mode="rb") as image_data:
            # Get result with faces
            detected_faces = self.__face_client.face.detect_with_stream(
                image = image_data,
                return_face_attributes = features,
                return_face_id = False
            )

            self.number_faces = len(detected_faces)

            # Ask if there is at least one detected face
            if len(detected_faces) > 0:
                self.summary_description = f"Detected faces: {len(detected_faces)}"
                print(f"Detected faces: {len(detected_faces)}")
                face_number = 1

                # Read image from file path (BGR format)
                image = cv2.imread(image_file)

                # Font configuration
                color = (255, 0, 0)
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 0.5
                thickness = 2

                # Process detected faces
                for f in detected_faces:
                    face = Face(face_number)
                    print(f"\nFace number {face_number}")

                    # Draw and annotate face
                    r = f.face_rectangle
                    cv2.rectangle(image, (r.left, r.top), (r.left + r.width, r.top + r.height), color, thickness)
                    
                    annotation = 'Face {}'.format(face_number)
                    cv2.putText(image, annotation, (r.left, r.top - 10), font, fontScale, color, thickness)

                    # Get face attributes
                    if f.face_attributes:
                        detected_attributes = f.face_attributes.as_dict()
                        
                        if "blur" in detected_attributes:
                            print("\n  Blur:")

                            face.blur = True
                            for blur_name in detected_attributes['blur']:
                                print('    - {}: {}'.format(blur_name, detected_attributes['blur'][blur_name]))
                                face.blur_features.append(f"{blur_name}: {detected_attributes['blur'][blur_name]}")
                        else:
                            print("\n  No blur feature detected")

                        if 'occlusion' in detected_attributes:
                            print("\n  Occlusion:")

                            face.occlusion = True
                            for occlusion_name in detected_attributes['occlusion']:
                                print('    - {}: {}'.format(occlusion_name, detected_attributes['occlusion'][occlusion_name]))
                                face.occlusion_features.append(f"{occlusion_name}: {detected_attributes['occlusion'][occlusion_name]}")
                        else:
                            print("\n  No occlusion feature detected")

                        if 'glasses' in detected_attributes:
                            face.glasses = True
                            face.glasses_features = f"Glasses: {detected_attributes['glasses']}"
                            print('\n  Glasses: {}'.format(detected_attributes['glasses']))
                        else:
                            print("\n  No glasses feature detected")

                    self.faces.append(face)
                    face_number += 1

                # Save image result to a file
                cv2.imwrite(output_file, image)
                print(f"Image save in {output_file}")

                with open(output_file, "rb") as f:
                    self.image_data_output = f.read()
                    
                # Open a window with the result
                if preview:
                    cv2.imshow("Preview", image)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
            else:
                print(f"No faces detected")
                self.summary_description = "No faces detected"

                with open(image_file, "rb") as f:
                    self.image_data_output = f.read()