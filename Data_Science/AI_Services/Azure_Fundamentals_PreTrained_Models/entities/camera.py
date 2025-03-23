from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis.models import VisualFeatures
import cv2

class Camera:
    '''
        Camera class that uses Azure AI Computer Vision to get insights from images.
        It uses OpenCV to work with images.
    '''
    
    def __init__(self, ai_endpoint, ai_key):
        # Client instance
        self.__cv_client = ImageAnalysisClient(
            endpoint = ai_endpoint,
            credential = AzureKeyCredential(ai_key)
        )

    def takePhoto(self, image_file):
        '''
            Read an image as binary from file path
        '''
        self.image_file = image_file
        with open(self.image_file, "rb") as f:
            self.image_data = f.read()

        if self.image_data:
            print("Image read")
    
    def getCaptions(self):
        '''
            Generate a caption of the image in natural language output
        '''
        print("Getting captions")

        # Get result with caption features
        result = self.__cv_client.analyze(
            image_data = self.image_data,
            visual_features = [VisualFeatures.CAPTION]
        )

        # Get image captions
        if result.caption is not None:
            self.caption = result.caption.text
            print("\nCaption found")
            print("\nCaption: '{}' (confidence: {:.2f}%)".format(result.caption.text, result.caption.confidence * 100))
        else:
            print("No caption found")

    def getDenseCaptions(self):
        '''
            Generate more detailed captions for the objects detected
        '''
        print("Getting dense captions")

        # Get result with dense caption features
        result = self.__cv_client.analyze(
            image_data = self.image_data,
            visual_features = [VisualFeatures.DENSE_CAPTIONS]
        )

        # Get image dense captions
        if result.dense_captions is not None:
            self.dense_captions = []

            print("\nDense caption found")
            print(f"\nTotal captions found: {len(result.dense_captions.list)}")
            for caption in result.dense_captions.list:
                self.dense_captions.append(caption.text)
                print("\nCaption: '{}' (confidence: {:.2f}%)".format(caption.text, caption.confidence * 100))
        else:
            print("No dense captions found")

    def getTags(self):
        '''
            Identify tags about the image, including objects, scenery, setting, and actions
        '''
        print("Getting tags")
        
        # Get result with tag features
        result = self.__cv_client.analyze(
            image_data = self.image_data,
            visual_features = [VisualFeatures.TAGS]
        )
        
        # Get image tags
        if result.tags is not None:
            self.tags = []

            print("\nTags found")
            print(f"\nTotal tags found: {len(result.tags.list)}")
            for tag in result.tags.list:
                self.tags.append(tag.name)
                print("\nTag: '{}' (confidence: {:.2f}%)".format(tag.name, tag.confidence * 100))
        else:
            print("No tags found")

    def getObjects(self, output_file, preview = False):
        '''
            Identify the bounding box for each detected object
        '''
        print("Getting objects")

        # Get result with object features
        result = self.__cv_client.analyze(
            image_data = self.image_data,
            visual_features = [VisualFeatures.OBJECTS]
        )

        # Get image objects
        if result.objects is not None:
            self.objects = []

            print("\Objects found")
            print(f"\nTotal objects found: {len(result.objects.list)}")

            # Read image from file path (BGR format)
            image = cv2.imread(self.image_file)

            # Font configuration
            color = (255, 0, 0)
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 0.5
            thickness = 2

            # Get image objects
            for detected_object in result.objects.list:
                self.objects.append(detected_object.tags[0].name)

                # Draw object bounding box
                r = detected_object.bounding_box
                cv2.rectangle(image, (r.x, r.y), (r.x + r.width, r.y + r.height), color, thickness)

                # Write down object tag
                cv2.putText(image, detected_object.tags[0].name, (r.x, r.y - 10), font, fontScale, color, thickness)

                print("\n{} (confidence: {:.2f}%)".format(detected_object.tags[0].name, detected_object.tags[0].confidence * 100))

            # Save image result
            cv2.imwrite(output_file, image)
            print(f"Image save in {output_file}")

            # Read output image in binary form to send to frontend
            with open(output_file, "rb") as f:
                self.image_data_output = f.read()

            # Open a window with the result
            if preview:
                cv2.imshow("Preview", image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        else:
            print("No objects found")

    def getPeople(self, output_file, preview = False):
        '''
            Identify the bounding box for detected people
        '''

        # Get result with people features
        result = self.__cv_client.analyze(
            image_data = self.image_data,
            visual_features = [VisualFeatures.PEOPLE]
        )

        # Get people
        if result.people is not None:
            print("\People found")
            print(f"\nTotal people found: {len(result.people.list)}")

            self.people = f"There are {len(result.people.list)} people."

            # Read image from file path (BGR format)
            image = cv2.imread(self.image_file)

            # Font configuration
            color = (255, 0, 0)
            thickness = 2

            # Get people
            for detected_people in result.people.list:
                # Draw object bounding box
                r = detected_people.bounding_box
                cv2.rectangle(image, (r.x, r.y), (r.x + r.width, r.y + r.height), color, thickness)

                print("\n{} (confidence: {:.2f}%)".format(detected_people.bounding_box, detected_people.confidence * 100))

            # Save image result to a file
            cv2.imwrite(output_file, image)
            print(f"Image save in {output_file}")

            # Read output image in binary form to send to frontend
            with open(output_file, "rb") as f:
                self.image_data_output = f.read()

            # Open a window with the result
            if preview:
                cv2.imshow("Preview", image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        else:
            print("No people found")

    def readText(self, output_file, preview = False):
        '''
            Identify the bounding box for detected texts
        '''
        
        # Get result with text features
        result = self.__cv_client.analyze(
            image_data = self.image_data,
            visual_features = [VisualFeatures.READ]
        )

        # Get text
        if result.read is not None:
            print("\Text found")

            self.text = []

            # Read image from file path (BGR format)
            image = cv2.imread(self.image_file)

            # Font configuration
            color = (0, 0, 255)
            thickness = 3

            if len(result.read.blocks) > 0:
                for idx, line in enumerate(result.read.blocks[0].lines):
                    # Return the text detected in the image
                    self.text.append(line.text)
                    print(f"Line {idx}: {line.text}")

                    # Draw object bounding box
                    r = line.bounding_polygon
                    #bounding_polygon = ((r[0].x, r[0].y),(r[1].x, r[1].y),(r[2].x, r[2].y),(r[3].x, r[3].y))
                    cv2.rectangle(image, (r[0].x, r[0].y), (r[2].x, r[2].y), color, thickness)

                # Save image result to a file
                cv2.imwrite(output_file, image)
                print(f"Image save in {output_file}")

                # Read output image in binary form to send to frontend
                with open(output_file, "rb") as f:
                    self.image_data_output = f.read()

                # Open a window with the result
                if preview:
                    cv2.imshow("Preview", image)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
            else:
                self.text.append("No text found")
                self.image_data_output = self.image_data
        else:
            self.image_data_output = self.image_data
            print("No text found")