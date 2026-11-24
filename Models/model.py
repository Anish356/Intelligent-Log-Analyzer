from langchain_openai import ChatOpenAI




model = ChatOpenAI(
    #model="llama-3.3-70b",
    model="gpt-oss-120b",
    base_url="https://model-broker.aviator-model.bp.anthos.otxlab.net/",
    api_key="sk-aOyZlqdsY0olzXjequGb2w",
    temperature=0,
)