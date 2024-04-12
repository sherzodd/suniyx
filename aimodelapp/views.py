import pickle
from fastai.vision.all import *
from rest_framework import views, serializers, status
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


# Load your model
model = pickle.load(open('your_model.pkl', 'rb'))


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
        prediction = model.predict(data['features'])
        results = {'prediction': prediction.tolist()}
        serializer = ResultSerializer(results)
        return Response(serializer.data, status=status.HTTP_200_OK)
