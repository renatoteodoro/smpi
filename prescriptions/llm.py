from django.conf import settings


def get_llm(streaming: bool = False):
    provider = getattr(settings, 'LLM_PROVIDER', 'openai')

    if provider == 'openai':
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=getattr(settings, 'LLM_MODEL', 'gpt-4o-mini'),
            api_key=getattr(settings, 'OPENAI_API_KEY', ''),
            streaming=streaming,
            temperature=0.1,
        )
    elif provider == 'local':
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=getattr(settings, 'LLM_MODEL', 'llama3'),
            streaming=streaming,
        )
    else:
        raise ValueError(f'Unknown LLM_PROVIDER: {provider}')


def get_streaming_llm():
    return get_llm(streaming=True)
