from PIL import Image
import requests
import torch
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
from visual_clues.models.blip import blip_decoder
import os
from pathlib import Path
import wget

class BLIP_Captioner():

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = "/inputs/blipcap-checkpoint/model_base_capfilt_large.pth"
        self.model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_capfilt_large.pth'
        self.image_size = 384
        self.vit = 'base'
        self.create_folder_for_cp()
        model = blip_decoder(pretrained=self.model_path, image_size=self.image_size, vit=self.vit)
        model.eval()
        self.model = model.to(self.device)

    def create_folder_for_cp(self):
        """
            Download the model checkpoint locally to a predefined path.
        """
        if not os.path.isfile(self.model_path):
            print("BLIP Checkpoints not found locally, Downloading in progres...")
            dirs_path = "/" + '/'.join(self.model_path.split("/")[1:-1]) + "/"
            Path(dirs_path).mkdir(parents=True, exist_ok=True)
            wget.download(self.model_url, dirs_path)
            print("Successfully downloaded BLIP checkpoints.")

    def process_frame(self, raw_image):

        raw_image = raw_image.convert('RGB')
        
        transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size),interpolation=InterpolationMode.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
            ]) 
        image = transform(raw_image).unsqueeze(0).to(self.device)   
        return image
    
    def generate_caption(self, frame):

        with torch.no_grad():
            # beam search
            caption = self.model.generate(frame, sample=False, num_beams=3, max_length=20, min_length=15) 
            # nucleus sampling
            # caption = model.generate(image, sample=True, top_p=0.9, max_length=20, min_length=5) 
            return caption[0]
    
    
