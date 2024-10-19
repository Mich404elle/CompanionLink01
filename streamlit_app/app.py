from dotenv import load_dotenv
import os
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
from pydub import AudioSegment
import numpy as np
import tempfile
from utils import scenarios, training_material, check_for_violations, chatbot_response, speech_to_text, text_to_speech, generate_feedback

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize session state to store conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "scenario_index" not in st.session_state:
    st.session_state["scenario_index"] = 0  # Start from the first scenario

if "warnings" not in st.session_state:
    st.session_state["warnings"] = 0  # Track the number of warnings

if "submitted" not in st.session_state:  # Initialize "submitted" variable
    st.session_state["submitted"] = False  # Track if the user has submitted a response

# Sidebar
section = st.sidebar.selectbox("Choose Section", ["Chat with Melissa", "Volunteer Guidance", "Guidance Chatbot", "Feedback"])

# Voice chat with Melissa using microphone input
if section == "Chat with Melissa":
    st.header("Chat with Melissa")

    # Use audio_recorder to record the user's voice
    audio_data = audio_recorder(
        pause_threshold=5.0,  # Maximum silence length before ending the recording
        energy_threshold=300,  # The threshold for detecting voice vs background noise
        text="Click to speak to Melissa",
        icon_size="2x"
    )

    # Check if audio data is recorded
    if audio_data is not None:
        st.audio(audio_data, format="audio/wav")  # Play the recorded audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            temp_wav.write(audio_data)
            # Transcribe using OpenAI Whisper
            transcribed_text = speech_to_text(temp_wav.name)
            st.write(f"You (transcribed): {transcribed_text}")

            st.session_state.conversation.append(f"You (transcribed): {transcribed_text}")

            bot_response = chatbot_response(transcribed_text)
            st.write(f"Melissa: {bot_response}")

            # Convert response to audio using TTS (synchronously)
            tts_audio = text_to_speech(bot_response)
            st.audio(tts_audio, format="audio/webm")
            st.session_state.conversation.append(f"Melissa (voice): {bot_response}")

    # Display the full conversation
    st.header("Conversation History")
    for message in st.session_state.conversation:
        st.write(message)

elif section == "Volunteer Guidance":
    st.header("Volunteer Guidance Material")
    st.write(training_material)

elif section == "Guidance Chatbot":
    st.header("Guidance Chatbot - Scenario Practice")

    # Display current scenario
    if st.session_state.scenario_index < len(scenarios):
        current_scenario = scenarios[st.session_state.scenario_index]
        st.write(f"Scenario {st.session_state.scenario_index + 1}: {current_scenario['scenario']}")

        # User input for response
        user_input = st.text_input("Your response:", key=f"response_{st.session_state.scenario_index}")

        # Submit response and move to the next scenario in one click
        if st.button("Submit and Next", key=f"submit_next_{st.session_state.scenario_index}"):
            if user_input:
                st.success("Thank you. Please compare your answer to the example question below.")
                st.write(f"Example Response: {current_scenario['correct_response']}")
                
                # Move to the next scenario immediately after submitting
                st.session_state.scenario_index += 1

    # End of scenarios
    if st.session_state.scenario_index >= len(scenarios):
        st.header("Scenario Practice Complete!")
        st.write(f"You completed all scenarios with {st.session_state.warnings} warnings in Melissa's chat.")

        # Option to reset and start over
        if st.button("Restart Practice", key="restart"):
            st.session_state.scenario_index = 0
            st.session_state.warnings = 0

elif section == "Feedback":
    st.header("Feedback on Your Conversation with Melissa")

    # Generate feedback based on the conversation
    if st.button("Generate Feedback"):
        if st.session_state.conversation:
            feedback = generate_feedback()
            st.write("### Feedback:")
            st.write(feedback)
        else:
            st.write("No conversation history available for feedback.")