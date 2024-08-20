class Face:
    def __init__(self, id):
        self.id = id
        self.occlusion = False
        self.blur = False
        self.glasses = False
        self.blur_features = []
        self.occlusion_features = []
        self.glasses_features = ""
        
    def to_dict(self):
        return {
            'id': self.id,
            'occlusion': self.occlusion,
            'blur': self.blur,
            'glasses': self.glasses,
            'blur_features': self.blur_features,
            'occlusion_features': self.occlusion_features,
            'glasses_features': self.glasses_features
        }