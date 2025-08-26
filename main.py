import streamlit as st
import openai
import re

st.set_page_config(page_title="TalentScout Hiring Assistant", layout="centered")

if "stage" not in st.session_state:
    st.session_state.stage = "greet"
if "candidate" not in st.session_state:
    st.session_state.candidate = {}
if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []
if "ended" not in st.session_state:
    st.session_state.ended = False

with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
    st.markdown("**TalentScout AI/ML Intern Assignment Demo**")

def chatbot_response(prompt, system_role=""):
    messages = []
    if system_role:
        messages.append({"role": "system", "content": system_role})
    messages += [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()

def generate_tech_questions(tech_stack, years):
    prompt = (
        f"Generate 4 concise technical interview questions evaluating a candidate's proficiency in the following technologies: {tech_stack}. "
        f"The questions should be suitable for {years} years experience level and cover programming, frameworks, databases, or tools as declared."
    )
    system_role = "You are an expert technical interviewer for a software company."
    resp = chatbot_response(prompt, system_role)
    return [q.strip("- \n") for q in resp.split("\n") if len(q.strip()) > 3]

end_keywords = ["exit", "quit", "bye", "end", "thank you", "thanks"]

def main():
    if st.session_state.ended:
        st.success("Thank you for completing the screening! Our team will review your responses and reach out for next steps.")
        st.balloons()
        return

    if st.session_state.stage == "greet":
        st.write("👋 **Welcome to TalentScout!**\nI'm your AI Hiring Assistant. I will guide you through a short screening process.\nType 'exit' anytime to end.")
        if st.button("Start"):
            st.session_state.stage = "get_name"

    elif st.session_state.stage in [
        "get_name", "get_email", "get_phone", "get_experience", "get_position", "get_location", "get_tech"
    ]:
        prompts = {
            "get_name": "Please enter your full name:",
            "get_email": "Enter your email address:",
            "get_phone": "Enter your phone number:",
            "get_experience": "How many years of work experience do you have?",
            "get_position": "What is your desired position?",
            "get_location": "Where are you currently located?",
            "get_tech": "List your tech stack (languages, frameworks, databases, tools):",
        }
        field_map = {
            "get_name": "name",
            "get_email": "email",
            "get_phone": "phone",
            "get_experience": "years",
            "get_position": "position",
            "get_location": "location",
            "get_tech": "tech_stack",
        }

        prompt_label = prompts[st.session_state.stage]
        input_key = f"input_{st.session_state.stage}"
        user_input = st.text_input(prompt_label, key=input_key)
        if user_input:
            if any(k in user_input.lower() for k in end_keywords):
                st.session_state.ended = True
            else:
                st.session_state.candidate[field_map[st.session_state.stage]] = user_input.strip()
                keys = list(prompts.keys())
                idx = keys.index(st.session_state.stage)
                if idx + 1 < len(keys):
                    st.session_state.stage = keys[idx + 1]
                else:
                    st.session_state.tech_questions = generate_tech_questions(
                        st.session_state.candidate["tech_stack"],
                        st.session_state.candidate["years"]
                    )
                    st.session_state.stage = "interview"

    elif st.session_state.stage == "interview":
        st.write("Thank you! Now, answer these technical questions to assess your skills.")
        all_answered = True
        for i, question in enumerate(st.session_state.tech_questions):
            answer_key = f"answer_{i}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = ""
            answer = st.text_input(f"Q{i+1}: {question}", key=answer_key)
            if answer == "":
                all_answered = False
            if any(k in answer.lower() for k in end_keywords):
                st.session_state.ended = True
                return

        if all_answered:
            if st.button("Finish"):
                for i in range(len(st.session_state.tech_questions)):
                    st.session_state.candidate[f"q{i+1}_ans"] = st.session_state[f"answer_{i}"]
                st.session_state.stage = "end"

    elif st.session_state.stage == "end":
        st.success("Thank you for completing the screening! Our team will review your responses and reach out for next steps.")
        st.balloons()
        st.session_state.ended = True

if __name__ == "__main__":
    main()
