from app.domain.chatbot.model import ChatBot


async def get_all_chatbots():
    return await ChatBot.all()


async def get_chatbot_by_id(id):
    return await ChatBot.filter(pk=id).first()


async def create_chatbot(chatbot_data):
    return await ChatBot.create(**chatbot_data.dict())


async def patch_chatbot_by_id(chatbot, update_chatbot):
    chatbot.step = update_chatbot.step
    chatbot.is_terminate = update_chatbot.is_terminate
    chatbot.selection_path = update_chatbot.selection_path
    chatbot.options = update_chatbot.options
    chatbot.answer = update_chatbot.answer

    await chatbot.save()

    return chatbot


async def delete_chatbot_by_id(chatbot):
    await chatbot.delete()
