import webbrowser 

def search_youtube(topic:str) -> None:
    """Search YouTube for a specific topic."""
    format_topic = "+".join(topic.split())
    link = f"https://www.youtube.com/results?search_query={format_topic}"
    try:
        webbrowser.open(link)
    except Exception as e:
        return f"Error occured in youtube search"
    return f"Your {topic} search results are ready."



