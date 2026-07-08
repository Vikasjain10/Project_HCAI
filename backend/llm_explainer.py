from openai import OpenAI

client = OpenAI(
    api_key="YOUR_KEY"
)

def explain_result(

    stress,

    fatigue,

    fatigue_type,

    wellness

):

    prompt = f"""

    Stress: {stress}

    Fatigue: {fatigue}

    Fatigue Type:
    {fatigue_type}

    Wellness:
    {wellness}

    Explain the user's condition.

    Give recommendations.

    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text