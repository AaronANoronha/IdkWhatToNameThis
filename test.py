import streamlit as st

form_count = 0

questions = []

def layer_func():
    global form_count
    with st.form(f"layer_func_{form_count}"):
        Question = st.text_area("Question")
        Answer = st.text_area("Answer")
        form_submit = st.form_submit_button("Submit")
        if form_submit:
            if Question != "":
                questions.append((Question, Answer))

                st.empty() # this line will remove the question input field
                if Answer != "":
                    st.success("Question and Answer generated successfully")
                    st.empty()  # this line will remove the answer input field
    form_count += 1

layer_func()

if st.sidebar.button('New Question'):
    layer_func()

st.write("All questions and answers:")
for question, answer in questions:
    st.write("Q: " + question)
    st.write("A: " + answer)