import uuid
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.integration_helper.models import Conversation
from apps.integration_helper.openai_utils import get_openai_response
from apps.integration_helper.prompt import PROMPT
from fyle_accounting_mappings.models import DestinationAttribute


def generate_dynamic_prompt(workspace_id):

    bank_accounts = list(DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type__in=['ACCOUNTS_PAYABLE', 'BANK_ACCOUNT']).values_list('value', flat=True))
    credit_card_accounts = list(DestinationAttribute.objects.filter(workspace_id=workspace_id, attribute_type='CREDIT_CARD_ACCOUNT').values_list('value', flat=True))

    bank_accounts_str = ', '.join(bank_accounts) if bank_accounts else "None available"
    credit_card_accounts_str = ', '.join(credit_card_accounts) if credit_card_accounts else "None available"

    dynamic_prompt = f"""
    {PROMPT}

    Don't give them options, try to match roughly to what they have added, if it doesn't match completely ask them 
    to provide the correct value by giving them options.
    Please match the provided bank account name to one of these available accounts: {bank_accounts_str}.
    Also, match the provided credit card account name to one of these: {credit_card_accounts_str}.
    """
    return dynamic_prompt

class ConversationViewSet(viewsets.ViewSet):
    """
    ViewSet for creating, retrieving, adding messages, and clearing conversations.
    """

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation and get the first OpenAI response.
        """
        content = request.data.get('content')

        if not content:
            return Response({"error": "content are required"}, status=status.HTTP_400_BAD_REQUEST)
        

        dynamic_prompt = generate_dynamic_prompt(kwargs['workspace_id'])
        conversation_id = str(uuid.uuid4())

        conversation = Conversation.objects.create(
            conversation_id=conversation_id, role='system', content=dynamic_prompt
        )

        conversation = Conversation.objects.create(
            conversation_id=conversation_id, role='user', content=content
        )
        messages = [{"role": "system", "content": dynamic_prompt}, {"role": "user", "content": content}]

        assistant_response = get_openai_response(messages)

        Conversation.objects.create(conversation_id=conversation_id, role="assistant", content=assistant_response)

        return Response({
            'conversation_id': conversation.conversation_id,
            'assistant_response': assistant_response
        }, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=["post"])
    def add_message(self, request, pk=None, *args, **kwargs):
        """
        Add a new message to an existing conversation using conversation_id and get an OpenAI response.
        """
        content = request.data.get("content")
        conversation_id = pk

        if not content:
            return Response(
                {"error": "content are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not Conversation.objects.filter(conversation_id=pk).first():
            return Response(
                {"error": "Conversation id doesn't exists!"}
            )
        
        messages = list(Conversation.objects.filter(conversation_id=conversation_id).values("role", "content").order_by('created_at'))

        messages.append({"role": "user", "content": content})
        Conversation.objects.create(conversation_id=conversation_id, role="user", content=content)


        assistant_response = get_openai_response(messages)
        Conversation.objects.create(conversation_id=conversation_id, role="assistant", content=assistant_response)
        
        return Response(
            {"assistant_response": assistant_response}, status=status.HTTP_201_CREATED
        )
    

    @action(detail=True, methods=["delete"])
    def clear(self, request, pk=None):
        """
        Clear the conversation history by deleting it using conversation_id.
        """
        conversation = Conversation.objects.filter(conversation_id=pk)
        if conversation.exists():
            conversation.delete()
            return Response(
                {"message": "Conversation cleared"}, status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Conversation not found"}, status=status.HTTP_404_NOT_FOUND
        )
