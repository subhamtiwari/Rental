import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
import openai # We still use the openai library
from openai import AuthenticationError, RateLimitError, APIConnectionError, OpenAIError # Keep these error types
import json # Import json library for formatting the fake data

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Get Groq API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
openai.api_key = groq_api_key # Set the key for the library globally (or per-request below)

# Check if Groq key exists
if not groq_api_key:
    print("CRITICAL: GROQ_API_KEY environment variable not set. LLM functionality WILL fail.")
else:
    print("Groq API Key found.")

# Define the Groq API endpoint
# openai.base_url = "https://api.groq.com/openai/v1" # Set base URL globally (alternative)

# --- Fake Apartment Database ---
# Let's represent the data as a dictionary
fake_apartment_data = {
    "community_name": "The Courtyard Apartments",
    "hours": "9 AM to 6 PM Monday to Friday, 10 AM to 4 PM Saturday. Closed Sunday.",
    "amenities": ["Swimming Pool", "Fitness Center", "Pet Park", "On-site Laundry", "Covered Parking"],
    "pet_policy": "We are pet friendly! We allow up to 2 pets per apartment with a $300 pet deposit and $35 monthly pet rent per pet. Breed restrictions apply.",
    "units": {
        "1B1B": {
            "name": "One Bedroom, One Bath",
            "sqft": 750,
            "price_range": "$1450 - $1550",
            "availability": "Limited - 2 available next month",
            "features": ["Balcony", "Walk-in Closet", "Dishwasher"]
        },
        "2B2B": {
            "name": "Two Bedroom, Two Bath",
            "sqft": 1100,
            "price_range": "$1800 - $1950",
            "availability": "Good - 5 available now",
            "features": ["Balcony", "Washer/Dryer Hookups", "Walk-in Closet", "Dishwasher"]
        },
        "Studio": {
            "name": "Studio",
            "sqft": 500,
            "price_range": "$1200 - $1300",
            "availability": "Waitlist only",
            "features": ["Dishwasher", "Large Closet"]
        }
    },
    "specials": "Offering one month free rent on select two-bedroom apartments with a 13-month lease!"
}
# Convert the dictionary to a JSON string for easier inclusion in the prompt
# Use indentation for better readability if needed in logs, but keep it compact for the prompt
fake_db_string = json.dumps(fake_apartment_data)
# ---------------------------

# --- Create OpenAI Client configured for Groq ---
# It's often better to create the client instance where needed or manage it within the app context,
# especially if you might switch between providers. Let's create it inside the function for now.
# client = openai.OpenAI(
#     api_key=groq_api_key,
#     base_url="https://api.groq.com/openai/v1",
# ) # Option 1: Create client instance here if preferred

# ---------------------

app = Flask(__name__)

# --- Helper Function for LLM Interaction ---
# Modify this function significantly
def get_llm_response(user_query):
    """Sends the user query + fake DB info to Groq API and gets a response."""
    # Ensure the key is loaded (redundant check if loaded globally)
    local_groq_api_key = os.getenv("GROQ_API_KEY")
    if not local_groq_api_key:
        print("LLM Error: No Groq API key configured.")
        return "I apologize, my connection to the AI brain is missing configuration."

    # Create a client instance configured for Groq *inside the function*
    # This ensures it uses the correct endpoint and key for this specific call.
    client = openai.OpenAI(
        api_key=local_groq_api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    try:
        print(f"Sending to Groq: '{user_query}'") # Log what we send
        # --- Updated Prompt with Database Context ---
        # Provide the fake database info as context for the LLM.
        # Instruct it to use this information to answer questions accurately.
        prompt = f"""
        You are a helpful AI assistant for the leasing office of "{fake_apartment_data['community_name']}".
        Use the following information about the community and available units to answer customer questions accurately and concisely.

        **Community Information:**
        ```json
        {fake_db_string}
        ```

        **Your Task:**
        - Answer questions based *only* on the information provided above.
        - If asked about specific pricing, refer to the 'price_range'. State that prices can change and a tour is recommended for exact quotes.
        - If asked about availability, use the 'availability' field.
        - Mention amenities, pet policy, or hours if asked.
        - If asked about something not in the provided information, say you don't have that specific detail but can help with other questions or schedule a tour.
        - If asked to book a tour, ask for preferred dates and times so a human agent can follow up.
        - Keep your response short and conversational for a voice call.

        **Customer Query:** "{user_query}"
        """
        # ---------------------------------------------

        # Use the client instance to make the call
        response = client.chat.completions.create(
            # Choose a model available on Groq (check their docs for latest)
            # Examples: "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"
            model="llama3-8b-8192",
            messages=[
                # Note: We are putting everything in the system prompt for this simple case.
                # For longer conversations or more complex data, managing context
                # within the message history might be better.
                {"role": "system", "content": prompt},
                # We can optionally add the user query again as a 'user' message,
                # but the prompt above already includes it. Test which works better.
                # {"role": "user", "content": user_query}
            ],
            temperature=0.5, # Slightly lower temperature for more factual answers from the data
            max_tokens=100 # Increase slightly to allow for more detailed answers from DB
        )
        llm_result = response.choices[0].message.content.strip()
        print(f"Received from Groq: '{llm_result}'") # Log what we receive
        return llm_result

    # Keep the same error handling, as Groq API mimics OpenAI errors
    except AuthenticationError as e:
        print(f"CRITICAL Groq Authentication Error: {e}")
        return "I'm sorry, there seems to be an issue with my connection credentials. Please notify the office staff."
    except RateLimitError as e:
        print(f"Groq Rate Limit Error: {e}")
        return "I'm experiencing high call volume right now. Please try again shortly."
    except APIConnectionError as e:
        print(f"Groq Connection Error: {e}")
        return "I'm having trouble connecting to the AI service. Please try again in a moment."
    except OpenAIError as e: # Catch Groq/OpenAI specific errors
        print(f"Groq API Error: {e}")
        if "billing" in str(e).lower() or "quota" in str(e).lower() or "limit" in str(e).lower():
             # Groq free tier might have limits
             return "There might be an issue with the service account or usage limits have been reached. Please inform the office staff."
        return "I encountered an unexpected issue with the AI service. Please try again."
    except Exception as e:
        print(f"Generic Error calling Groq: {e}")
        return "I'm sorry, I encountered an error trying to understand that. Could you please repeat?"

# -------------------------------------------

# Basic route to check if the server is running
@app.route('/')
def home():
    return "Leasing Agent AI Backend is running!"

# Route to handle incoming calls from Twilio
@app.route("/voice", methods=['POST'])
def voice():
    """Respond to incoming phone calls, greet, and gather speech."""
    resp = VoiceResponse()
    resp.say("Hello! Thank you for calling the leasing office.", voice='alice')
    gather = Gather(input='speech', action='/process-speech', speechTimeout='auto', method='POST')
    gather.say("How can I help you today?", voice='alice')
    resp.append(gather)
    return Response(str(resp), mimetype='text/xml')

# Route to process the speech gathered from the user
@app.route("/process-speech", methods=['POST'])
def process_speech():
    """Process the speech input, get LLM response, respond, and gather again."""
    resp = VoiceResponse()
    speech_result = request.values.get('SpeechResult', None)
    confidence = request.values.get('Confidence', 0.0)
    print(f"Received speech: '{speech_result}' with confidence: {confidence}")

    response_spoken = False # Flag to track if we generated a spoken response

    if speech_result:
        llm_response_text = get_llm_response(speech_result)
        if llm_response_text:
            # Tell Twilio to say the LLM's response
            resp.say(llm_response_text, voice='alice')
            response_spoken = True
        else:
             print("Warning: LLM response was empty.")
             resp.say("I received your message, but I don't have a response right now.", voice='alice')
             response_spoken = True # We still spoke *something*
    else:
        print("No speech result received or confidence too low.")
        resp.say("I'm sorry, I didn't catch that. Could you please repeat?", voice='alice')
        response_spoken = True # We spoke an error message

    # --- Start Conversation Loop ---
    # Instead of hanging up, ask the user if there's anything else
    # and gather their next input, sending it back to this same function.
    gather = Gather(input='speech', action='/process-speech', speechTimeout='auto', method='POST')

    # Add a prompt to the gather, like asking "What else?"
    # Only add a pause if we actually spoke a response before this gather.
    if response_spoken:
        gather.pause(length=1) # Brief pause after the AI speaks
    gather.say("Is there anything else I can help you with?", voice='alice')
    resp.append(gather)

    # --- Add a fallback if gather fails ---
    # If the user says nothing after the "Anything else?" prompt,
    # we can say goodbye and hang up.
    resp.say("Thank you for calling. Goodbye!", voice='alice')
    resp.hangup()
    # --------------------------------

    # The TwiML now instructs Twilio to:
    # 1. Say the LLM response (if any)
    # 2. Pause briefly
    # 3. Ask "Is there anything else..."
    # 4. Listen for speech (and send it back to /process-speech if heard)
    # 5. If nothing heard, say Goodbye and Hangup.
    return Response(str(resp), mimetype='text/xml')


if __name__ == "__main__":
    app.run(debug=True, port=8080) 