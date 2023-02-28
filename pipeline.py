from textblob import TextBlob
import cleantext
import plotly.express as px
import pandas as pd
import streamlit as st
st.header("Customer Review Analyysis")
if st.checkbox("Please check this if you have a CSV available to be analysed", False, key=0):
    with st.spinner("Loading App..."):
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
                    col_to_predict = st.selectbox("Select the column to predict sentiment for", df.columns)
                    df['review_body'] = df[col_to_predict].astype(str)
                    df['score'] = df['review_body'].apply(score)
                    df['analysis'] = df['score'].apply(analyze)
                else:
                    st.write("Please upload a file to continue.")

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

        if upl:
            sentiments = df['analysis'].value_counts()
            if 'sentiments' in locals() or 'sentiments' in globals():
                fig = px.pie(sentiments, values=sentiments.values, names=sentiments.index)
            else:
                print("")
            if st.checkbox("Show pie chart"):
                st.plotly_chart(fig)
            else:
                st.write("Pie chart is hidden")

            if st.sidebar.checkbox("Review Filter", True, key=3):

                if not upl:
                    st.write("Please upload the file")
                elif "df" not in locals():
                    st.write("Please upload the file")
                else:
                    filter_ = st.selectbox("Filter by Sentiment", ['All'] + df["analysis"].unique().tolist())

                if "filter_" not in locals():
                    st.write()
                else:
                    if filter_ == 'All':
                        filtered_df = df
                    else:
                        filtered_df = df[df['analysis'] == filter_]
                    st.write(filtered_df)
            else:
                filtered_df = df[df["analysis"] == filter_]
                st.write(filtered_df)
            if st.sidebar.checkbox("Show/hide Sentiment Summary", True, key=4):
                with st.expander('Summary of reviews', expanded=True):
                    if "df" not in locals():
                        st.write("Please upload the file")
                    else:
                        pos = len(df[df["analysis"] == "Positive"])
                        neg = len(df[df["analysis"] == "Negative"])
                        neu = len(df[df["analysis"] == "Neutral"])
                        st.sidebar.write("Sentiment Summary:")
                        st.sidebar.write(f"Total Reviews :", pos + neg + neu)
                        st.sidebar.write(f"Positive:", pos)
                        st.sidebar.write(f"Negative:", neg)
                        st.sidebar.write(f"Neutral:",neu)

if st.checkbox("Please check this if you have a URL from which you want to import review data from", False, key=5):
    with st.spinner("Loading App..."):
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd
        import streamlit as st
        from textblob import TextBlob


        url = st.text_input("Enter product review URL:")
        page_num = int(st.number_input("Enter number of pages to scrape:", value=10))

        # Validate URL
        if not url.startswith("https://"):
            st.write("")
        else:
            data = []
            for i in range(1, page_num + 1):
                # URL setup and HTML request
                r = requests.get(url + '&pageNumber=' + str(i))
                soup = BeautifulSoup(r.text, 'html.parser')
                reviews = soup.find_all('div', {'data-hook': 'review'})

                for item in reviews:
                    review = {
                        'title': item.find('a', {'data-hook': 'review-title'}).text.strip() if item.find('a', {
                            'data-hook': 'review-title'}) else None,
                        'text': item.find('span', {'data-hook': 'review-body'}).text.strip() if item.find('span', {
                            'data-hook': 'review-body'}) else None,
                    }
                    if review['text'] is not None:
                        data.append(review)

            df = pd.DataFrame(data)
            if 'text' in df.columns:
                df['sentiment'] = df['text'].apply(lambda x: TextBlob(x).sentiment[0])
            else:
                df['sentiment'] = df['title'].apply(lambda x: TextBlob(x).sentiment[0])

            df['sentiment_label'] = df['sentiment'].apply(
                lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

            import plotly.express as px

            labels = df['sentiment_label'].value_counts().index
            values = df['sentiment_label'].value_counts().values

            # Make sure negative label is included in the labels and values lists
            if 'Negative' not in labels:
                labels = list(labels) + ['Negative']
                values = list(values) + [0]

            fig = px.pie(names=labels, values=values)
            if st.checkbox("Show pie chart"):
                st.plotly_chart(fig)
            else:
                st.write("Pie chart is hidden")

            # Total number of reviews
            total_reviews = df.shape[0]
            st.sidebar.write("Total Reviews:", total_reviews)

            # Number of unique positive, negative, and neutral reviews
            positive_reviews = df[df['sentiment_label'] == "Positive"].shape[0]
            negative_reviews = df[df['sentiment_label'] == "Negative"].shape[0]
            neutral_reviews = df[df['sentiment_label'] == "Neutral"].shape[0]

            st.sidebar.write("Positive Reviews:", positive_reviews)
            st.sidebar.write("Negative Reviews:", negative_reviews)
            st.sidebar.write("Neutral Reviews:", neutral_reviews)

            # Add a filter to select sentiment label
            sentiment_filter = st.selectbox("Filter by Sentiment:", ["All", "Positive", "Negative", "Neutral"])

            if sentiment_filter == "Positive":
                df = df[df['sentiment_label'] == "Positive"]
            elif sentiment_filter == "Negative":
                df = df[df['sentiment_label'] == "Negative"]
            elif sentiment_filter == "Neutral":
                df = df[df['sentiment_label'] == "Neutral"]

            st.write(df)

            if st.button('Download as CSV'):
                st.write(df.to_csv(index=False))









