import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY')
ALIBABA_API_KEY = os.getenv('ALIBABA_API_KEY')
K2_API_KEY = os.getenv('K2_API_KEY')

K2_BASE_URL = os.getenv('K2_BASE_URL')
ALIBABA_BASE_URL = os.getenv('ALIBABA_BASE_URL')
MINIMAX_BASE_URL = os.getenv('MINIMAX_BASE_URL')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL')
ZHIPU_BASE_URL = os.getenv('ZHIPU_BASE_URL')

LOCAL_BASE_URL = os.getenv('LOCAL_BASE_URL')
DAYTONA_API_KEY = os.getenv('DAYTONA_API_KEY')
DAYTONA_BASE_URL = os.getenv('DAYTONA_BASE_URL')

if __name__ == '__main__':
    print(ALIBABA_BASE_URL)
    print(ALIBABA_API_KEY[:20]+".....")
    print(ZHIPU_API_KEY[:20]+".....")
    print(ZHIPU_BASE_URL)

    # llm  = ChatOpenAI(
    #     model="glm-5.1",
    #     temperature=0.3,
    #     openai_api_key=ZHIPU_API_KEY,
    #     openai_api_base=ZHIPU_BASE_URL,
    #     max_tokens=2560000,
    # )
    llm = ChatOpenAI(
        model="deepseek-v4-pro",
        temperature=1.1,
        openai_api_key=DEEPSEEK_API_KEY,
        openai_api_base=DEEPSEEK_BASE_URL,
        max_tokens=2560000,
        model_kwargs={
            "extra_body": {
                "thinking": {"type": "disabled"}
            }
        }
    )

    response = llm.invoke("Hello, how are you?")

    print(response)