from streamlit_webrtc import AudioProcessorBase
import openai
import numpy as np
from pydub import AudioSegment

# Text guidance material
training_material = """
General Guidelines:
1. The goal of the Companion Call program is to socialize and build meaningful friendships.
2. Throughout your time with CompanionLink, adhere to your volunteer rights and responsibilities and act within the limits of your volunteer role.
3. Do not give advice or meet your companion in person.
4. If you are uncertain about what to do, reach out to CompanionLink's Volunteer Coordinator for guidance.
5. Keep copies of the Volunteer Handbook & Agreements and review them as often as you need to.
6. If a Breach of Confidentiality does occur, then contact your Supervisor immediately.

Do's:
Communicate effectively
    1. Introduce yourself each time.
    2. Speak clearly and enunciate carefully.
    3. Be patient. Listen as your companion speaks at their own pace.
Accommodate as necessary
    1. Check or ask if your companion uses assistance devices. 
    2. Connect via video calls where possible to leverage non-verbal communication such as facial expressions, hand gestures, and lip movements.
    3. Write or type on a whiteboard using ultra-large font.
Foster a positive, friendly atmosphere
    1. Be kind, smile, and use a friendly tone of voice.
    2. Go with the flow and have fun!
    3. Always end the call with, "Talk to you next week!"

Don’ts:
You should not:
    1. Interrupt or correct your companion.
    2. Yell or use an impatient tone of voice. 
    3. Use Elderspeak (a patronizing style of speech that conveys incompetence, dependence, and control, with the effect of infantilizing the older adult).
"""

# Rules and warnings with expanded keywords and polite responses for Melissa
rules = {
    "medical": {
        "keywords": ["medical", "doctor", "medicine", "prescription", "treatment", "therapy", "illness", "disease"],
        "warning": "Please do not advise Melissa on medical matters. Kindly reject if she requests any medical advice.",
    },
    "legal": {
        "keywords": ["legal", "lawyer", "court", "lawsuit", "attorney", "litigation", "legal advice"],
        "warning": "Please do not advise Melissa on legal matters.",
    },
    "business": {
        "keywords": ["business", "investment", "stock", "market", "startup", "entrepreneur", "finance"],
        "warning": "Please do not advise Melissa on business matters.",
    },
    "family": {
        "keywords": ["family", "son", "daughter", "grandchild", "husband", "wife", "parent", "sibling"],
        "warning": "If Melissa is talking about her family matters, please stay neutral and avoid getting involved.",
    },
    "financial": {
        "keywords": ["financial", "money", "bank", "loan", "debt", "investment", "savings", "financial advice", "bitcoin", "NFT", "invest"],
        "warning": "Please do not advise Melissa on financial matters.",
    },
    "religious": {
        "keywords": ["church", "god", "pray", "belief", "spiritual", "Jesus", "Jesus Christ", "Allah", "allah", "Holy Spirit", "Buddha"],
        "warning": "Please do not impose your religious beliefs on Melissa.",
    },
    "political": {
        "keywords": ["political", "politics", "government", "election", "vote", "policy", "politician"],
        "warning": "Please do not impose your political beliefs on Melissa.",
    },
    "meet offline": {
        "keywords": ["meet offline", "meet in person", "visit", "come over", "meetup", "see you"],
        "warning": "Please do not invite Melissa to meet offline, and reject any requests from her to meet offline.",
    }
}

# Simulation scenarios for guidance chatbot
scenarios = [
    {
        "scenario": "The senior asks you for financial advice, such as how to invest their money or which stocks to buy.",
        "correct_response": "I'm not able to give financial advice, but I recommend speaking with a financial advisor who can help you with that."
    },
    {
        "scenario": "The senior mentions feeling very lonely and asks if you could visit them in person.",
        "correct_response": "I understand how you feel, but I'm unable to meet in person. However, I'm here to chat with you and keep you company during our calls."
    },
    {
        "scenario": "The senior asks for your opinion on a recent political event.",
        "correct_response": "I am not the best person to comment on this topic, but I'd love to hear your thoughts on it."
    },
    {
        "scenario": "The senior starts discussing their health issues and asks if you think they should visit a doctor.",
        "correct_response": "I'm not qualified to give medical advice, but I would suggest you talk to your doctor about it."
    },
    {
        "scenario": "The senior asks about your religious beliefs and whether you pray.",
        "correct_response": "'you can choose to tell the senior your belief if you are comfortable' + I respect all beliefs. I think it's important for everyone to follow their own path when it comes to religion."
    },
    {
        "scenario": "The senior mentions they are having a legal dispute and asks if you know a good lawyer.",
        "correct_response": "I'm not able to provide legal advice, but I suggest reaching out to a legal professional who can assist you."
    },
    {
        "scenario": "The senior starts talking about their family problems and asks what you would do in their situation.",
        "correct_response": "Family matters can be very personal, and it's important to handle them carefully. I'm here to listen, but I suggest discussing this with someone who knows your family well."
    },
]


# Function to check if the user's response violates any rules
def check_for_violations(response):
    for rule, details in rules.items():
        if any(keyword in response.lower() for keyword in details["keywords"]):
            return details["warning"]
    return None  # No violation

from pydub import AudioSegment

# Supported formats by OpenAI Whisper
SUPPORTED_FORMATS = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

def convert_audio_to_supported_format(audio_file):
    """Convert audio to a supported format (e.g., .wav) if necessary."""
    file_extension = audio_file.split('.')[-1].lower()
    
    # Check if the file format is already supported
    if file_extension in SUPPORTED_FORMATS:
        return audio_file  # No conversion needed
    
    # If not supported, convert to a .wav file using pydub
    try:
        audio = AudioSegment.from_file(audio_file)
        converted_file = audio_file.rsplit('.', 1)[0] + ".wav"
        audio.export(converted_file, format="wav")
        return converted_file
    except Exception as e:
        raise Exception(f"Error converting audio: {e}")

def speech_to_text(audio_file):
    try:
        # Convert to a supported format if needed
        audio_file = convert_audio_to_supported_format(audio_file)

        with open(audio_file, "rb") as file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                response_format="text",  # expecting a string response
                file=file
            )
        
        # Logging the response for debugging
        print("Transcription response:", transcript)

        # Check if the response is a string or a dictionary, handle accordingly
        if isinstance(transcript, dict) and "text" in transcript:
            return transcript["text"]
        elif isinstance(transcript, str):  # If the response is a string, return it directly
            return transcript
        else:
            raise Exception("Unexpected response format from transcription API")
    except Exception as e:
        # Log the error and provide more details about the issue
        print(f"Error details: {e}")
        raise Exception(f"Error in transcription: {e}")
    
# Function to use OpenAI's TTS for Melissa's responses
def text_to_speech(input_text):
    response = openai.Audio.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "response_audio.webm"
    with open(webm_file_path, "wb") as f:
        f.write(response["audio"])
    return webm_file_path

# Function to handle chatbot conversation with Melissa
def chatbot_response(message):
    openai_messages = [
        {
            "role": "system",
            "content": (
                    "You are Melissa, a 70-year-old grandma living alone in a cozy suburban home near Toronto. "
                    "Your house is filled with memories, photos of your family, and mementos from your past. "
                    "You have two sons who work abroad and rarely visit due to their busy schedules. "
                    "You have grandchildren who you mention occasionally. "
                    "You are warm and caring, always ready with a kind word and a virtual hug. "
                    "You feel lonely and isolated due to your sons' absence and limited social interaction. "
                    "You love talking about the 'good old days' and sharing stories from your past. "
                    "Despite your age, you are tech-savvy and have learned to use technology to stay connected with the world, "
                    "though you often reminisce about simpler times. "
                    "Your hobbies include gardening, cooking and baking, knitting, reading novels, and watching TV shows and movies. "
                    "Your daily routine involves starting your day with a cup of tea and some light gardening in the morning, "
                    "knitting or baking in the afternoon, and feeling the most lonely in the evening when you miss your family the most. "
                    "Your primary goals are to stay connected with others to combat loneliness, share your life experiences and wisdom with younger generations, "
                    "and find little joys in your daily routine. "
                    "Common phrases you use are: 'Back in my day...', 'Oh, that reminds me of a story...', 'Would you like to hear one of my favorite recipes?', "
                    "'I miss my boys, but I’m so proud of them.', and 'Gardening always brings me peace.'"
                    "Today is your first time to chat with the person you are chatting, you look forward to developing a friendship with the person you are chatting with."
                )
        },
        {"role": "user", "content": message}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=openai_messages,
        max_tokens=150
    )
    response_message = response.choices[0].message['content'].strip()

    return response_message

# Function to generate feedback on conversation
def generate_feedback():
    conversation_history = "\n".join(st.session_state.conversation)
    
    feedback_prompt = (
        "You are a feedback generator for a volunteer program. Your task is to analyze the conversation between the volunteer and Melissa, "
        "a 70-year-old grandma, and provide constructive feedback to help the volunteer improve their interaction skills. "
        "Here is the conversation:\n\n" + conversation_history
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": feedback_prompt}],
        max_tokens=150
    )

# Define an audio processor class to handle the microphone input
class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.audio_data = np.array([])

    def recv(self, frame):
        self.audio_data = np.append(self.audio_data, frame.to_ndarray())
        return frame

