from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from oneid.serializers import CodeSerializer

@swagger_auto_schema(
    method='post',
    request_body=CodeSerializer(),
    responses={200: "Success"},
    tags=["oneid"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_oneid_token(request):

    serializer = CodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    code = serializer.validated_data["code"]

    response_data = {
        'token': code,
        'status': 200,
        "data": {
            "code": code,
            "message": "success",
        }
    }

    return Response(response_data)
