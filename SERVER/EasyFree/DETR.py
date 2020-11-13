# 필요 패키지
# torch
# torchvision
# albumentations

import sys
import torch
import torch.nn as nn
import numpy as np
from PIL import Image
from torchvision import transforms
import albumentations as A

model_name = 'detr_resnet50'

CATEGORY_NUMBER = ['N/A', '6000095799', '6000096206', '6000095904', '6000095829', '6000096294', '6000096175', '6000096220', '6000095921']

def show_pred(outputs):
    oboxes = outputs['pred_boxes'][0].detach().cpu().numpy()
    oboxes = [np.array(box).astype(np.int32) for box in A.augmentations.bbox_utils.denormalize_bboxes(oboxes, 512, 512)]
    
    prob   = outputs['pred_logits'].softmax(-1).detach().cpu().numpy()[0, :, :-1] # 멀티클래스 분류
    color = (220,0,0)
    for box,p in zip(oboxes,prob):
        cl = p.argmax()
        if p[cl] > 0.5:
            try:
                x1, x2, y1, y2 = box[0]-box[2], box[0]+box[2], box[1]-box[3], box[1]+box[3]
                print(x1, x2, y1, y2, CATEGORY_NUMBER[cl])
            except:pass

def DETRModel(num_classes,model_name=model_name):
    model = torch.hub.load('facebookresearch/detr', model_name, pretrained=False, num_classes=num_classes)
    def parameter_groups(self):
        return { 'backbone': [p for n,p in self.named_parameters()
                              if ('backbone' in n) and p.requires_grad],
                 'transformer': [p for n,p in self.named_parameters() 
                                 if (('transformer' in n) or ('input_proj' in n)) and p.requires_grad],
                 'embed': [p for n,p in self.named_parameters()
                                 if (('class_embed' in n) or ('bbox_embed' in n) or ('query_embed' in n)) 
                           and p.requires_grad]}
    setattr(type(model),'parameter_groups',parameter_groups)
    return model

class DETRModel(nn.Module):
    def __init__(self,num_classes=1):
        super(DETRModel,self).__init__()
        self.num_classes = num_classes
        
        self.model = torch.hub.load('facebookresearch/detr', model_name, pretrained=True)
        
        self.out = nn.Linear(in_features=self.model.class_embed.out_features,out_features=num_classes+1)
        
    def forward(self,images):
        d = self.model(images)
        d['pred_logits'] = self.out(d['pred_logits'])
        return d
    
    def parameter_groups(self):
        return { 
            'backbone': [p for n,p in self.model.named_parameters()
                              if ('backbone' in n) and p.requires_grad],
            'transformer': [p for n,p in self.model.named_parameters() 
                                 if (('transformer' in n) or ('input_proj' in n)) and p.requires_grad],
            'embed': [p for n,p in self.model.named_parameters()
                                 if (('class_embed' in n) or ('bbox_embed' in n) or ('query_embed' in n)) 
                           and p.requires_grad],
            'final': self.out.parameters()
            }

model = DETRModel(num_classes=9) # 나중에 모델 수정 시 변경
ORIGINAL_PATH = 'C:/Users/ehhah/dev/NLP_workspace/EasyFree/EasyFree-Backend/SERVER/EasyFree/detr_final.pth'
model.load_state_dict(torch.load(ORIGINAL_PATH))
model.to(torch.device('cuda'))
None

# 들어온 데이터 (임시)
img = Image.open('C:/Users/ehhah/dev/NLP_workspace/EasyFree/EasyFree-Backend/SERVER/EasyFree/uploads/image.png')
img = img.resize((512,512))
pil_to_tensor = transforms.ToTensor()(img).unsqueeze_(0)
dev_images = [img.to(torch.device('cuda')) for img in pil_to_tensor]
model.eval()
with torch.no_grad():
    outputs = model(dev_images)
outputs = {k: v.cpu() for k, v in outputs.items()}
show_pred(outputs)