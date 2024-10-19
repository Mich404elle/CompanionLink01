# CompanionLink Chatbot

## Overview:
  This is a project created for volunteer training, aims to utilize OpenAI's LLM for providing an interactive experience that mimic real live chat with a senior person.

## Structure
  This project was initially built with Flask app and later was converted to Streamlit with a better interfacea and new features. 

CompanionLink_chatbot/
├── flask_app/
│   ├── app_flask.py
│   ├── templates/
├── streamlit_app/
│   ├── app.py
│   ├── utils.py
│   ├── .env
├── myenv/
├── .gitignore
    
## Explanation
  flask_app
  The Flask app uses simple interface and text-based output, containing the following parts:

  1. Guidance: a text guidance to remind users basic principles and rules when chatting with the seniors.

  2. Chat Guidance: a chatbot that guide users through different scenarios that they might come across during their chat with the seniors. This chatbot provides example answers and suggestions to handel each scenarios.

  3. Chat with Melissa: an AI chatbot prompted to function as a 70-year-old Grandma with reminding mechanism for potential rules violation and feedback generation.

 streamlit_app (currently under development)
 The streamlit app incorperated text-to-speech and speech-to text api for real-time voice chatting function.

  1. Guidance: a text guidance to remind users basic principles and rules when chatting with the seniors. (same as the flask app)

  2. Chat Guidance: a chatbot that guide users through different scenarios that they might come across during their chat with the seniors. This chatbot provides example answers and suggestions to handel each scenarios. (same as the flask app)

  3. Chat with Melissa: an AI chatbot prompted to function as a 70-year-old Grandma with real-time voice chatting function and reminding mechanism for potential rules violation and feedback generation.
