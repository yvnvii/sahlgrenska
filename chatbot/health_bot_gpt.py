import openai

# ✅ Set the API key directly when initializing the client
client = openai.OpenAI(api_key="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")

def chat_with_gpt(user_input):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful and friendly health assistant. "
                    "The user will describe their health and lifestyle. "
                    "You will extract relevant data (age, gender, BMI, habits, family history), assess risks (like diabetes or cardiovascular issues), "
                    "and give personalized recommendations such as DNA testing, insurance advice, hospital checkups, or lifestyle changes."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


def run_health_chatbot():
    print("🧠 Welcome to your AI Health Assistant (GPT-powered)")
    print("Tell me about your health, lifestyle, and family medical history.\n")
    
    user_input = input("📝 You: ")

    print("\n🤖 Analyzing...\n")
    response = chat_with_gpt(user_input)

    print("✅ Here's your personalized health overview:\n")
    print(response)
    print("\n🩺 Note: This is not medical advice. Please consult a doctor for clinical care.")


if __name__ == "__main__":
    run_health_chatbot()
