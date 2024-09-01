import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocessor(data)  # Preprocess the data

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
        ax.plot(timeline['time'], timeline['message'], color='green', marker='o')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Messages')
        ax.set_title('Monthly Message Count')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black', marker='o')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Messages')
        ax.set_title('Daily Message Count')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        st.pyplot(fig)

        # Activity Map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.weak_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            ax.bar(busy_day.index, busy_day.values, color=plt.cm.plasma(busy_day.values / max(busy_day.values)))
            ax.set_xlabel('Day of the Week')
            ax.set_ylabel('Number of Messages')
            ax.set_title('Messages by Day of the Week')
            plt.xticks(rotation=45)
            plt.grid(axis='y')
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            ax.bar(busy_month.index, busy_month.values, color=plt.cm.plasma(busy_month.values / max(busy_month.values)))
            ax.set_xlabel('Month')
            ax.set_ylabel('Number of Messages')
            ax.set_title('Messages by Month')
            plt.xticks(rotation=45)
            plt.grid(axis='y')
            plt.tight_layout()
            st.pyplot(fig)

        # Weekly Activity Map
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap)
        ax.set_title('Activity Heatmap')
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Day of the Week')
        plt.xticks(rotation=90)
        plt.yticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig)

        # Finding the busiest users in the group (Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots(figsize=(12, 8), dpi=100)

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color=plt.cm.plasma(x.values / max(x.values)))
                ax.set_xlabel('Users')
                ax.set_ylabel('Number of Messages')
                ax.set_title('Messages by User')
                plt.xticks(rotation='vertical')
                plt.grid(axis='y')
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        try:
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
            ax.imshow(df_wc)
            ax.axis('off')
            st.pyplot(fig)
        except FileNotFoundError:
            st.error("The file 'stop_hinglish.txt' was not found. Please upload it or remove the dependency.")

        # Most common words
        st.title('Most Common Words')
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
        ax.barh(most_common_df[0], most_common_df[1])
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Words')
        ax.set_title('Most Common Words')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Emoji analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f%%", colors=plt.cm.plasma(range(len(emoji_df[0].head()))))
            ax.set_title('Emoji Distribution')
            st.pyplot(fig)
