import pickle
from fastai.vision.all import *
from rest_framework import views, serializers, status
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import torch
print(torch.__version__)
print(torch.cuda.is_available())

# Load your model
model = torch.load(open('aimodelapp/image_based_v3.pkl', 'rb'),  map_location=torch.device('cpu'))


# Define a serializer
class ResultSerializer(serializers.Serializer):
    prediction = serializers.ListField()  # Adjust field types as needed
    # Add more fields if necessary


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class PredictView(views.APIView):
    def post(self, request):
        image_file = request.FILES['image']
        img = Image.open(image_file)
        data = request.data
        pred, pred_id, probs = model.predict(img)
        prediction = "Null"
        if pred == 'Advertisement':  # predict bo’yicha ekranga ma’lumot berish kodlari
            print(f"bashorat: Reklama.")
            print(f"aniqlilik darajasi: {probs[pred_id] * 100:.1f}%")
            prediction = f"bashorat: Reklama. Aniqlilik darajasi: {probs[pred_id] * 100:.1f}%"
        elif pred == 'Content':
            print(f"bashorat: Content.")
            print(f"aniqlilik darajasi: {probs[pred_id] * 100:.1f}%")
            prediction = f"bashorat: Content. Aniqlilik darajasi: {probs[pred_id] * 100:.1f}%"
        else:
            print('No Data')

        results = {'prediction': prediction}
        serializer = ResultSerializer(results)
        return Response(serializer.data, status=status.HTTP_200_OK)
