TEMP_ALL_FUNCTIONS = {
    "tools": [
        {"name": "weather_report", "description": "Get the current weather for a location.", "parameters": {"location": "string", "required": ["location"]}},
        {"name": "get_stock_data", "description": "Fetch stock market data for an exchange.", "parameters": {"exchange": "string", "required": ["exchange"]}},
        {"name": "search_youtube", "description": "Search YouTube for a specific topic.", "parameters": {"topic": "string", "required": ["topic"]}},
        {"name": "news_headlines", "description": "Fetch top news headlines.", "parameters": {}},
        {"name": "yt_download", "description": "Download a YouTube video.", "parameters": {}},
        {"name": "send_to_ai", "description": "Handle creative prompts like jokes or stories.", "parameters": {"prompt": "string", "required": ["prompt"]}},
        {"name": "app_runner", "description": "Open the specified application by name. For example, you can say 'open WhatsApp' or 'run Chrome'.", "parameters": {"app_name": "string", "required": ["app_name"]}},
        {"name": "open_github", "description": "Open GitHub in a web browser.", "parameters": {}},
        {"name": "open_instagram", "description": "Open Instagram in a web browser.", "parameters": {}},
        {"name": "open_youtube", "description": "Open YouTube in a web browser.", "parameters": {}},
        {"name": "private_mode", "description": "Search in the incognito or private mode for specific topic","parameters":{"topic":"string" , "required":["topic"]}},
        {"name": "make_a_call","description": "make a phone call to provided contact name." , "parameters":{"name":"string" , "required":["name"]}},
        {"name": "send_email","description":"send email on gmail","parameters":{}},
        {"name": "duckgo_search","description":"search provided query on internet for quick information.","parameters":{"query":"string" , "required":["query"]}},
        {"name": "chat_with_rag","description":"For Depper and insgithfull discussions using (RAG)." , "parameters":{"subject":"string" , "required":["subject"]}}
    ]
}

## Format for functions for llm using pydanctic 
# dict : "OBJECT"
# list : "ARRAY"
# str : "STRING
# int: "INTEGER"
# float : "NUMBER"  

ALL_FUNCTIONS = {
    "tools": [
        {
            "name": "weather_report",
            "description": "Get the current weather for a location.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "location": {"type": "STRING"}
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_stock_data",
            "description": "Fetch stock market data for an exchange.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "exchange": {"type": "STRING"}
                },
                "required": ["exchange"]
            }
        },
        {
            "name": "search_youtube",
            "description": "Search YouTube for a specific topic.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "topic": {"type": "STRING"}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "news_headlines",
            "description": "Fetch top news headlines."
        },
        {
            "name": "yt_download",
            "description": "Download a YouTube video."
        },
        {
            "name": "personal_chat_ai",
            "description": "Engage in an empathetic conversation, recalling stored personal information. Use this for questions about the user's memories, goals, feelings, or identity, such as 'What is my name?' or 'Tell me a memory.' Ensure responses are contextually relevant.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "first_query": {"type": "STRING"}
                },
                "required": ["first_query"]
            }
        },
        {
            "name": "send_to_ai",
            "description": "Handle creative prompts like jokes or stories.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "prompt": {"type": "STRING"}
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "app_runner",
            "description": "Open an app if installed, otherwise open the website version. Example: 'Open Spotify' will try the app first, then the web.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "app_name": {"type": "STRING"}
                },
                "required": ["app_name"]
            }
        },
        {
            "name": "private_mode",
            "description": "Search in incognito or private mode for a specific topic.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "topic": {"type": "STRING"}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "make_a_call",
            "description": "Make a phone call to the provided contact name.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"}
                },
                "required": ["name"]
            }
        },
        {
            "name": "send_email",
            "description": "Send an email on Gmail."
        },
        {
            "name": "duckgo_search",
            "description": "Search the provided query on the internet for quick information.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "chat_with_rag",
            "description": "For deeper and insightful discussions on specific topic using (RAG).",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "subject": {"type": "STRING"}
                },
                "required": ["subject"]
            }
        }
    ]
}

##############################
ALL_FUNCTIONS = {
    "tools": [
        {
            "name": "data_analysis",
            "description": "Tool for answering numerical and comparative data analysis queries involving calculations, comparisons, trends, plot graphs , filtering and aggregations.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "user_query": {"type": "STRING","description": "The data analysis question."}
                },
                "required": ["user_query"]
            }
        },
        {
            "name": "weather_report",
            "description": "Get real-time weather details for a given location.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "location": {"type": "STRING", "description": "City name or coordinates (e.g., 'New York' or '37.7749,-122.4194')."}
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_stock_data",
            "description": "Retrieve stock market data for a given exchange (e.g., NASDAQ, NYSE, NSE).",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "exchange": {"type": "STRING", "description": "Stock exchange name or symbol (e.g., 'NASDAQ')."}
                },
                "required": ["exchange"]
            }
        },
        {
            "name": "search_youtube",
            "description": "Find YouTube videos related to a specific topic.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "topic": {"type": "STRING", "description": "Search keyword or phrase (e.g., 'AI tutorials')."}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "news_headlines",
            "description": "Fetch the latest top news headlines from various sources.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "yt_download",
            "description": "Download a YouTube video using a valid YouTube URL.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "url":{"type": "STRING","description":"Youtube video url "}
                },
                "required": ["url"]
            }
        },
        {
            "name": "personal_chat_ai",
            "description": "Engage in a personal AI-driven conversation, recalling user memories and details.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "User's question related to personal information (e.g., 'What is my name?')."}
                },
                "required": ["query"]
            }
        },
        {
            "name": "send_to_ai",
            "description": "Generate AI-based responses for creative tasks like jokes, poems, or short stories.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "prompt": {"type": "STRING", "description": "Creative request (e.g., 'Tell me a joke','stories' etc)."}
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "app_runner",
            "description": "Open a desktop or mobile app if installed; otherwise, launch the web version.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "app_name": {"type": "STRING", "description": "App name (e.g., 'Spotify', 'YouTube')."}
                },
                "required": ["app_name"]
            }
        },
        {
            "name": "private_mode",
            "description": "Perform an internet search in incognito/private mode.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "Search term (e.g., 'best VPN services')."}
                },
                "required": ["query"]
            }
        },
        {
            "name": "make_a_call",
            "description": "Make a phone call to a specific contact.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "contact_name": {"type": "STRING", "description": "Name of the contact (e.g., 'John Doe')."}
                },
                "required": ["contact_name"]
            }
        },
        {
            "name": "send_email",
            "description": "Compose and send an email using Gmail.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "recipient": {"type": "STRING", "description": "Email address of the recipient (e.g., 'example@gmail.com')."},
                    "subject": {"type": "STRING", "description": "Email subject line."},
                    "body": {"type": "STRING", "description": "Content of the email message."}
                },
                "required": ["recipient", "subject", "body"]
            }
        },
        {
            "name": "duckgo_search",
            "description": "Perform a web search using DuckDuckGo for uptodate internet infromation.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "Search keyword or phrase."}
                },
                "required": ["query"]
            }
        },
        {
            "name": "chat_with_rag",
            "description": "Engage in deep , research-based discussions using a Retrieval-Augmented Generation (RAG) model.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "subject": {"type": "STRING", "description": "Word Topic for discussion (e.g., 'Quantum Computing' , 'disaster')."}
                },
                "required": ["subject"]
            }
        }
    ]
}

UI_ALL_FUNCTIONS = {
        "tools": [
        {
            "name": "weather_report",
            "description": "Get real-time weather details for a given location.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "location": {"type": "STRING", "description": "City name or coordinates (e.g., 'New York' or '37.7749,-122.4194')."}
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_stock_data",
            "description": "Retrieve stock market data for a given exchange (e.g., NASDAQ, NYSE, NSE).",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "exchange": {"type": "STRING", "description": "Stock exchange name or symbol (e.g., 'NASDAQ')."}
                },
                "required": ["exchange"]
            }
        },
        {
            "name": "search_youtube",
            "description": "Find YouTube videos related to a specific topic.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "topic": {"type": "STRING", "description": "Search keyword or phrase (e.g., 'AI tutorials')."}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "news_headlines",
            "description": "Fetch the latest top news headlines from various sources.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "yt_download",
            "description": "Download a YouTube video using a valid YouTube URL.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "url":{"type": "STRING","description":"Youtube video url "}
                },
                "required": ["url"]
            }
        },
        {
            "name": "send_to_ai",
            "description": "Generate AI-based responses for creative tasks like jokes, poems, or short stories.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "prompt": {"type": "STRING", "description": "Creative request (e.g., 'Tell me a joke','stories' etc)."}
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "app_runner",
            "description": "Open a desktop or mobile app if installed; otherwise, launch the web version.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "app_name": {"type": "STRING", "description": "App name (e.g., 'Spotify', 'YouTube')."}
                },
                "required": ["app_name"]
            }
        },
        {
            "name": "private_mode",
            "description": "Perform an internet search in incognito/private mode.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "Search term (e.g., 'best VPN services')."}
                },
                "required": ["query"]
            }
        },
        {
            "name": "make_a_call",
            "description": "Make a phone call to a specific contact.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "contact_name": {"type": "STRING", "description": "Name of the contact (e.g., 'John Doe')."}
                },
                "required": ["contact_name"]
            }
        },
        {
            "name": "send_email",
            "description": "Compose and send an email using Gmail.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "recipient": {"type": "STRING", "description": "Email address of the recipient (e.g., 'example@gmail.com')."},
                    "subject": {"type": "STRING", "description": "Email subject line."},
                    "body": {"type": "STRING", "description": "Content of the email message."}
                },
                "required": ["recipient", "subject", "body"]
            }
        },
        {
            "name": "duckgo_search",
            "description": "Perform a web search using DuckDuckGo for uptodate internet infromation.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "Search keyword or phrase."}
                },
                "required": ["query"]
            }
        }
    ]
}


UI_ALL_FUNCTIONS_EXAMPLE = """
User Query: What's the weather in London?  
Expected JSON Output:
```json
[
   {{
     "name": "weather_report",
     "parameters": {{"location": "London"}}
   }}
]
```

User Query: open chrome for me 
Expected JSON Output:
```json
[
   {{
     "name": "app_runner",
     "parameters": {{"app_name": "chrome"}}
   }}
]
```

User Query: Open YouTube.  
Expected JSON Output:
```json
[
   {{
     "name": "app_runner",
     "parameters": {{"app_name":"youtube"}}
   }}
]
```

```
User Query: Tell me a joke.  
Expected JSON Output:
```json
[
   {{
     "name": "send_to_ai",
     "parameters": {{"prompt": "Tell me a joke"}}
   }}
]
```

User Query: Get news headlines and then let's discuss about life.  
Expected JSON Output:
```json
[
   {{
     "name": "news_headlines",
     "parameters": {{}}
   }},
   {{
     "name": "send_to_ai",
     "parameters": {{"prompt":"discuss various aspects of life"}}
   }}
]
```

User Query: Get stock data for NASDAQ and then search YouTube for NASDAQ analysis.  
Expected JSON Output:
```json
[
   {{
     "name": "get_stock_data",
     "parameters": {{"exchange": "NASDAQ"}}
   }},
   {{
     "name": "search_youtube",
     "parameters": {{"topic": "NASDAQ analysis"}}
   }}
]
```

User Query: Who will win the FIFA World Cup in 2030?  
Expected JSON Output:
```json
[
   {{
     "name": "duckgo_search",
     "parameters": {{"query": "FIFA World Cup winners in 2030?"}}
   }}
]
```

User Query: Get stock data for NASDAQ and then Open Instagram web.  
Expected JSON Output:
```json
[
   {{
     "name": "get_stock_data",
     "parameters": {{"exchange": "NASDAQ"}}
   }},
   {{
     "name": "app_runner",
     "parameters": {{"app_name":"instagram"}}
   }}
]
```

User Query: Who is the current president of Brazil?  
Expected JSON Output:
```json
[
  {{
    "name": "duckgo_search",
    "parameters": {{"query": "current president of Brazil?"}}
  }}
]
```
"""


ALL_FUNCTIONS_EXAMPLE = """"
User Query: What's the weather in London?  
Expected JSON Output:
```json
[
   {{
     "name": "weather_report",
     "parameters": {{"location": "London"}}
   }}
]
```

User Query: open chrome for me 
Expected JSON Output:
```json
[
   {{
     "name": "app_runner",
     "parameters": {{"app_name": "chrome"}}
   }}
]
```
User Query: total sum of Filled Jobs.  
Expected JSON Output:
```json
[
   {{
     "name": "data_analysis",
     "parameters": {{"user_query":"total sum of Filled Jobs."}}
   }}
]
```
User Query: Open YouTube.  
Expected JSON Output:
```json
[
   {{
     "name": "app_runner",
     "parameters": {{"app_name":"youtube"}}
   }}
]
```


User Query: What do you remember about me? 
Expected JSON Output:
```json
[
  {{
    "name": "personal_chat_ai",
    "parameters": {{"query": "what you know about me?"}}
  }}
]
```
User Query: Tell me a joke.  
Expected JSON Output:
```json
[
   {{
     "name": "send_to_ai",
     "parameters": {{"prompt": "Tell me a joke"}}
   }}
]
```

User Query: Let's discuss the ethical implications of AI in detail.  
Expected JSON Output:
```json
[
   {{
     "name": "chat_with_rag",
     "parameters": {{"subject": "AI"}}
   }}
]
```

User Query: Get news headlines and then let's discuss about life.  
Expected JSON Output:
```json
[
   {{
     "name": "news_headlines",
     "parameters": {{}}
   }},
   {{
     "name": "chat_with_rag",
     "parameters": {{"subject": "life"}}
   }}
]
```

User Query: Get stock data for NASDAQ and then search YouTube for NASDAQ analysis.  
Expected JSON Output:
```json
[
   {{
     "name": "get_stock_data",
     "parameters": {{"exchange": "NASDAQ"}}
   }},
   {{
     "name": "search_youtube",
     "parameters": {{"topic": "NASDAQ analysis"}}
   }}
]
```

User Query: Who will win the FIFA World Cup in 2030?  
Expected JSON Output:
```json
[
   {{
     "name": "duckgo_search",
     "parameters": {{"query": "FIFA World Cup winners in 2030?"}}
   }}
]
```

User Query: Get stock data for NASDAQ and then Open Instagram web.  
Expected JSON Output:
```json
[
   {{
     "name": "get_stock_data",
     "parameters": {{"exchange": "NASDAQ"}}
   }},
   {{
     "name": "app_runner",
     "parameters": {{"app_name":"instagram"}}
   }}
]
```

User Query: Discuss the philosophical implications of quantum mechanics.  
Expected JSON Output:
```json
[
  {{
    "name": "chat_with_rag",
    "parameters": {{"subject": "quantum mechanics"}}
  }}
]
```

User Query: Who is the current president of Brazil?  
Expected JSON Output:
```json
[
  {{
    "name": "duckgo_search",
    "parameters": {{"query": "current president of Brazil?"}}
  }}
]
```
"""




CURRENT_ALL_FUNCTIONS =[
        {"name": "weather_report", "description": "Get real-time weather details for a given location.", "arguments": {"location": "STRING"}},
        {"name": "search_youtube", "description": "Find videos related to a specific topic.", "arguments": {"topic": "STRING"}},
        {"name": "news_headlines", "description": "Fetch the latest top news headlines from various sources.", "arguments": {}},
        {"name": "yt_download", "description": "Download a YouTube video using a valid YouTube URL.", "arguments": {}},
        {"name": "send_to_ai", "description": "Generate AI-based responses for creative tasks like jokes, poems, short stories or Reasoning. ", "arguments": {"prompt": "STRING"}},
        {"name": "app_runner", "description": "Open a desktop or mobile app if installed; otherwise, launch the web version.", "arguments": {"app_name": "STRING"}},
        {"name": "private_mode", "description": "Perform an internet search in incognito/private mode.","arguments":{"query":"STRING"}},
        {"name": "make_a_call","description": "Make a phone call to a specific contact." , "arguments":{"contact_name":"STRING"}},
        {"name": "send_email","description":"Compose and send an email using Gmail.","arguments":{"recipient":"STRING" , "subject":"STRING","body":"STRING"}},
        {"name": "duckgo_search","description":"Perform a web search using DuckDuckGo for uptodate internet information.","arguments":{"query":"STRING"}},
] 
