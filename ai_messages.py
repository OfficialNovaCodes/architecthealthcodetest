import openai
import logging
import os

#from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#load_dotenv(dotenv_path='archtest.env') - used for local development. archtest.env is not pushed to the github repo.
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # Via environment variable

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def ai_generation(prompt):
    try:
        chat_completion = client.chat.completions.create(
        messages=[
            {
            "role": "user",
            "content": (prompt)
            }
        ],
            model="gpt-4o",
            temperature=0.4
    )
        if chat_completion and chat_completion.choices:
            response_text = chat_completion.choices[0].message.content
            return response_text
        else:
            logging.error("No response from OpenAI.")
            return "Error: No response from OpenAI."
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"Error: {e}"

def ai_analysis(data):
       
    prompt_base_path = os.path.join('prompt_base.txt')
    
    with open(prompt_base_path, 'r', encoding='utf-8') as file:
        base_prompt = file.read()
    
    data_str = "\n".join([str(item) for item in data])

    final_prompt = base_prompt + "\n\n CDC Information: " + data_str
    print(final_prompt)

    analysis = ai_generation(final_prompt)
    print(analysis)
    return analysis

    
