import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }

    try:
        body = request.get_json()
        prompt = body.get("prompt")
        stream_enabled = body.get("stream")

        if not stream_enabled:
            return {
                "statusCode": 400,
                "body": "Streaming must be enabled"
            }

        def generate():
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior data analyst. Analyze survey results and provide 7 key insights with supporting evidence. Minimum 700 characters."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    stream=True
                )

                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield f"data: {json.dumps({'choices':[{'delta':{'content': content}}]})}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
            "body": generate()
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }