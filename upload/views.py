from rest_framework import views
from rest_framework.response import Response
import cloudinary.uploader
from backend_ecommerce.helpers import custom_response

class UploadImageAPIView(views.APIView):
    def post(self, request):
        try:
            file = request.FILES['file']
            upload_result = cloudinary.uploader.upload(file)
            return custom_response('Upload image successfully!', 'Success', upload_result['url'], 201)
        except Exception as e:
            return custom_response('Upload image failed!', 'Error', str(e), 400)