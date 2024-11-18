import os
import json
from openai import OpenAI
from .translate_utils import array_to_dictionary

openai_client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
)

'''
Translate character scripts and sound effects to Korean using ChatGPT.
and try to make dictionary with returned gpt answer(string)

Caution:
- use this function with try/except code.
- if gpt answer with other string, not only json format,
  this function can make error
- check return type
  (string: error message, dictionary: translated strings)
'''
def translate_to_korean(character_scripts = [], sound_effect = []):
    prompt = make_prompt(character_scripts, sound_effect)

    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    try:
        ret = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError as e:
        return f"Json decode error (not json format): {e}"
    except:
        return f"Unexpected error: {e}"

    return ret

def make_prompt(cs = [], se = []):
    default_prompt = "일본 만화의 대사, 효과음을 한국 만화처럼 자연스럽게 번역해서 코드 형식 없이 JSON 형식으로의 문자열만 전달해줘."
    
    cs_prompt = array_to_dictionary(cs)
    se_prompt = array_to_dictionary(se)

    prompt = f"""
{default_prompt}
{{
    scripts: {cs_prompt},
    effects: {se_prompt}
}}
"""
    return prompt