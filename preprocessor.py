import re
import pandas as pd

def preprocessor(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    
    # Split data based on the pattern
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create dataframe
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date's data_type
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract user_name and message
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)  # Use raw string here
        if entry[1:]:  # User name
            users.append(entry[1].strip())
            messages.append(" ".join(entry[2:]).strip())
        else:
            users.append('group_notification')
            messages.append(entry[0].strip())

    # Making new Columns
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Additional date-time columns for analysis
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create a 'period' column for time-based analysis
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour + 1}")

    df['period'] = period

    return df
