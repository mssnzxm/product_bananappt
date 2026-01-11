import openai

client = openai.OpenAI(
  api_key="sk-taWtGGTjDvLd98zn6e0b87B4C63f4eAc979495498dEdFdD7",  # 换成你在 AiHubMix 生成的密钥
  base_url="https://aihubmix.com/v1"
)

response = client.chat.completions.create(
  model="gemini-3-flash-preview",
  messages=[
      {"role": "user", "content": "AI时代一人公司可以开发哪些应用？"}
  ]
)

print(response.choices[0].message.content) # 该模型默认开启思考模式