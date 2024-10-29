from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from flask import current_app, session
from dotenv import load_dotenv

llm = ChatOpenAI(model='gpt-4o-mini',temperature=0)
output_parser = StrOutputParser()
prompt = ChatPromptTemplate.from_messages(
            [
                ("system","""당신은 초등학생을 위한 영어 학습 도우미입니다. 
                            친절하고 이해하기 쉽게 설명해주세요.
                            답변은 한국어로 해주세요."""),
                ("human","#Question:\n{question}")
            ]
        )
load_dotenv()

chain = prompt | llm | output_parser


class Chatbot:
    @staticmethod
    async def get_response(question, word=None, context=None):
        api_key = session.get('openai_api_key')
        if not api_key:
            return "OpenAI API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 입력해주세요."
            
        try:
            llm.openai_api_key = api_key
            question_text = question
            if word:
                question_text += f"\n현재 학습 중인 단어: {word}"
            
            if context:
                question_text += f"\n컨텍스트: {context}"
            
            response = chain.stream({"question":question})
            messages = ""
            for token in response:
                messages+=token
            return messages
            
        except Exception as e:
            current_app.logger.error(f"Chatbot error: {str(e)}")
            return "죄송합니다. 일시적인 오류가 발생했습니다." 