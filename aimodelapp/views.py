import pickle
from fastai.vision.all import *
from torchvision import transforms  # Add this import statement
from rest_framework import views, serializers, status
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import torch
import pathlib

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath


# Load your model
# model = pickle.load(open('image_based_v3.pkl', 'rb'))

class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else:
            return super().find_class(module, name)


model = CPU_Unpickler(open('image_based_v3.pkl', 'rb')).load()
device = torch.device('cpu')
model = model.to(device)


# Define a serializer
class ResultSerializer(serializers.Serializer):
    prediction = serializers.ListField()


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class PredictView(views.APIView):
    def post(self, request):
        print(request.FILES.keys())
        print(request.FILES)

        image_file = request.FILES['image']
        img = Image.open(image_file)

        # Transform the image to match the preprocessing done during training
        transform = transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor()
        ])

        img = transform(img)
        img = img.unsqueeze(0)
        img = img.to(device)
        with torch.no_grad():
            model.eval()  # Set the model to evaluation mode
            output = model(img)
            preds = output.argmax(dim=1)

        # Process the predictions
        if preds == 0:  # Assuming your model outputs class indices
            pred_label = 'Advertisement'
        elif preds == 1:
            pred_label = 'Content'
        else:
            pred_label = 'Unknown'

        prediction = f"Prediction: {pred_label}"

        results = {'prediction': prediction}
        serializer = ResultSerializer(results)
        return Response(serializer.data, status=status.HTTP_200_OK)
