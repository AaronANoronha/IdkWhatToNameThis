from textblob import TextBlob
import cleantext
import plotly.express as px
import pandas as pd
import streamlit as st
st.header('Sentiment Analysis')
if st.sidebar.checkbox("Text Input", True, key=1):
 with st.expander('Analyze Text',expanded=False):
    text = st.text_input('Text here: ')
    if text:
        if isinstance(text, str):
            blob = TextBlob(text)
            polarity = round(blob.sentiment.polarity, 2)
            subjectivity = round(blob.sentiment.subjectivity, 2)
            st.write('Polarity: ', polarity)
            st.write('Subjectivity: ', subjectivity)

            if polarity >= 0.5:
                sentiment = "Positive"
            elif polarity == 0:
                sentiment = "Neutral"
            else:
                sentiment = "Negative"
            st.write('Sentiment: ', sentiment)
        else:
            st.write("Error: Input text is not a string.")

    pre = st.text_input('Clean Text: ')
    if pre:
        st.write(cleantext.clean(pre, clean_all=False, extra_spaces=True,
                                 stopwords=True, lowercase=True, numbers=True, punct=True))

if st.sidebar.checkbox("Csv Upload", True, key=2):
    with st.expander('Analyze CSV', expanded=True):

        upl = st.file_uploader('Upload file')


        def score(x):
            blob1 = TextBlob(str(x))
            return blob1.sentiment.polarity


        def analyze(x):
            if x >= 0.5:
                return 'Positive'
            elif x == 0:
                return 'Neutral'
            else:
                return 'Negative'


        if upl:
            df = pd.read_excel(upl)
            df['review_body'] = df['review_body'].astype(str)
            df['score'] = df['review_body'].apply(score)
            df['analysis'] = df['score'].apply(analyze)
        else:
            st.write("Please upload a file to continue.")

with st.expander("Show Data", expanded=False):
    if 'df' in locals():
        st.write(df.head(6))
    else:
        st.write("No data available.")

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

if 'df' in locals():
    csv = convert_df(df)
    st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='sentiment.csv',
                    mime='text/csv',
                )


if st.sidebar.checkbox("Review Filter", False, key=3):
    with st.expander("Filter the Reviews",expanded=True):
        if not upl:
            st.write("Please upload the file")
        elif "df" not in locals():
            st.write("Please upload the file")
        else:
            filter_ = st.selectbox("Filter by Sentiment", df["analysis"].unique())

if "filter_" not in locals():
    st.write()
else:
 filtered_df = df[df["analysis"] == filter_]
 st.write(filtered_df)
if st.sidebar.checkbox("Show/hide Sentiment Summary", False, key=4):
    with st.expander('Summary of reviews',expanded=True):
        if "df" not in locals():
            st.write("Please upload the file")
        else:
         pos = len(df[df["analysis"] == "Positive"])
         neg = len(df[df["analysis"] == "Negative"])
         neu = len(df[df["analysis"] == "Neutral"])
         st.write("Sentiment Summary:")
         st.write(f"Total Reviews : {pos + neg +neu}")
         st.write(f"Positive: {pos}")
         st.write(f"Negative: {neg}")
         st.write(f"Neutral: {neu}")
        if upl:
            sentiments = df['analysis'].value_counts()
            fig = px.pie(sentiments, values=sentiments.values, names=sentiments.index)
            st.plotly_chart(fig)



