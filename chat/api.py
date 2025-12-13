from django.http import JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Conversation, ConversationMessage
from .serializers import ConversationListSerializer, ConversationDetailSerializer, ConversationMessageSerializer 

from useraccount.models import User


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def conversations_list(request):
    # Get the user ID from the request (from Authorization header)
    auth = JWTAuthentication()
    try:
        auth_result = auth.authenticate(request)
        if auth_result:
            user, validated_token = auth_result
            current_user_id = user.id
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
    except Exception as e:
        print(f'Auth error: {e}')
        return JsonResponse({'error': f'Authentication failed: {str(e)}'}, status=401)
    
    user = User.objects.get(pk=current_user_id)
    serializer = ConversationListSerializer(user.conversations.all(), many=True)

    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def conversations_detail(request, pk):
    # Get the user ID from the request (from Authorization header)
    auth = JWTAuthentication()
    try:
        auth_result = auth.authenticate(request)
        if auth_result:
            user, validated_token = auth_result
            current_user_id = user.id
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
    except Exception as e:
        print(f'Auth error: {e}')
        return JsonResponse({'error': f'Authentication failed: {str(e)}'}, status=401)
    
    try:
        conversation = Conversation.objects.get(pk=pk, users__id=current_user_id)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)

    conversation_serializer = ConversationDetailSerializer(conversation, many=False)
    messages_serializer = ConversationMessageSerializer(conversation.messages.all(), many=True)

    return JsonResponse({
        'conversation': conversation_serializer.data, 
        'messages': messages_serializer.data
    }, safe=False) 

@api_view(['GET']) 
@authentication_classes([])
@permission_classes([])
def conversations_start(request, user_id):
    # Get the user ID from the request (from Authorization header)
    auth = JWTAuthentication()
    try:
        auth_result = auth.authenticate(request)
        if auth_result:
            user, validated_token = auth_result
            current_user_id = user.id
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
    except Exception as e:
        print(f'Auth error: {e}')
        return JsonResponse({'error': f'Authentication failed: {str(e)}'}, status=401)
    
    conversations = Conversation.objects.filter(users__in=[user_id]).filter(users__in=[current_user_id])

    if conversations.count() > 0:
        conversation = conversations.first()
        
        return JsonResponse({'success': True, 'conversation_id': conversation.id}) 
    else:
        other_user = User.objects.get(pk=user_id) 
        current_user = User.objects.get(pk=current_user_id)
        conversation = Conversation.objects.create()
        conversation.users.add(current_user)
        conversation.users.add(other_user)

        return JsonResponse({'success': True, 'conversation_id': conversation.id})