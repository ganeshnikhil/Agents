# from src.Brain.hippocampus import AnteriorCingulateCortex, Hippocampus


# non_reasoning_model = "gemma3:4b"
# temperature = 0


# hippocampus_in = Hippocampus(
#             model=non_reasoning_model,
#             temperature=temperature,
#             prompt_path="./src/prompts/memory_prompts/memory_in.txt"
# )
# hippocampus_out = Hippocampus(
#             model=non_reasoning_model,
#             temperature=temperature,
#             prompt_path="./src/prompts/memory_prompts/memory_out.txt"
# )


# test_queries = [
#     "I cleaned the kitchen counter.",
#     "I remembered my first trip abroad.",
#     "I had dinner with friends yesterday.",
# ]

# user_query = [
#     "Did I water the plants today?",
#     "Do I have any phobias?",
#     "Did I go for a walk yesterday?",
#     "What is the weather like tomorrow?",
#     "what is my name",
#     "how many friends do i have",
#     "when is my birthday",
#     "is there any metting at 2 am today",
#     "Did I lock the front door?",
#     "Did I pay the electricity bill?",
#     "Did I drink water this morning?",
# ]

# for query in user_query:
#     mem_type = hippocampus_out.gateway_router(query)
#     print(f"{query} : {mem_type.get('memory_type')} : {mem_type.get('reason')}")

# user_queries = [
#     "I cleaned the kitchen counter.",
#     "I remembered my first trip abroad.",
#     "I had dinner with friends yesterday.",
# ]

# for query in user_queries:
#     mem_type = hippocampus_in.gateway_router(query)
#     print(f"{query} : {mem_type.get('memory_type')} : {mem_type.get('reason')}")


new_data = [
    # Personal Information Storage/Retrieval (Long-term Memory)
    ("Store my new phone number: +1-555-0123.", 0, 1, 0),
    ("What's my phone number?", 1, 1, 0),
    ("Remember my email: john.doe@email.com.", 0, 1, 0),
    ("What email address do I use?", 1, 1, 0),
    ("Save my home address: 123 Oak Street, Boston.", 0, 1, 0),
    ("Where do I live?", 1, 1, 0),
    ("Note that my birthday is March 15, 1990.", 0, 1, 0),
    ("When is my birthday?", 1, 1, 0),
    ("Remember my wife's name is Sarah.", 0, 1, 0),
    ("What's my wife's name?", 1, 1, 0),
    
    # Work/Professional Information
    ("Store my employee ID: EMP-7845.", 0, 1, 0),
    ("What's my employee ID?", 1, 1, 0),
    ("Remember I work at TechCorp Solutions.", 0, 1, 0),
    ("Where do I work?", 1, 1, 0),
    ("Save my manager's name: Lisa Thompson.", 0, 1, 0),
    ("Who is my manager?", 1, 1, 0),
    ("Note that my work hours are 9 AM to 5 PM.", 0, 1, 0),
    ("What are my work hours?", 1, 1, 0),
    ("Remember my salary is $75,000.", 0, 1, 0),
    ("What's my current salary?", 1, 1, 0),
    
    # Medical Information
    ("Store my doctor's name: Dr. Martinez.", 0, 1, 0),
    ("Who is my doctor?", 1, 1, 0),
    ("Remember I'm allergic to peanuts.", 0, 1, 0),
    ("What allergies do I have?", 1, 1, 1),
    ("Save my blood type: O-negative.", 0, 1, 0),
    ("What's my blood type?", 1, 1, 0),
    ("Note that I take medication for high blood pressure.", 0, 1, 0),
    ("What medications do I take?", 1, 1, 1),
    ("Remember my insurance policy number: INS-9876.", 0, 1, 0),
    ("What's my insurance policy number?", 1, 1, 0),
    
    # Financial Information
    ("Store my bank account number: 123456789.", 0, 1, 0),
    ("What's my bank account number?", 1, 1, 0),
    ("Remember my credit score is 750.", 0, 1, 0),
    ("What's my credit score?", 1, 1, 0),
    ("Save my investment portfolio value: $50,000.", 0, 1, 0),
    ("What's my investment portfolio worth?", 1, 1, 0),
    ("Note my monthly rent is $1,200.", 0, 1, 0),
    ("How much is my monthly rent?", 1, 1, 0),
    ("Remember I have a car loan of $15,000.", 0, 1, 0),
    ("What outstanding loans do I have?", 1, 1, 1),
    
    # Short-term Memory Operations
    ("Remember I have a meeting at 3 PM today.", 0, 0, 0),
    ("When is my meeting today?", 1, 0, 0),
    ("Note that I left my keys on the kitchen counter.", 0, 0, 0),
    ("Where did I put my keys?", 1, 0, 0),
    ("Store the WiFi password for today: Guest2024.", 0, 0, 0),
    ("What's the WiFi password I saved earlier?", 1, 0, 0),
    ("Remember the parking spot number is B-47.", 0, 0, 0),
    ("Which parking spot am I in?", 1, 0, 0),
    ("Note that I ordered pizza for lunch.", 0, 0, 0),
    ("What did I order for lunch?", 1, 0, 0),
    
    # Immediate Knowledge Queries (Current)
    ("What's the capital of France?", 2, 2, 0),
    ("How many seconds are in a minute?", 2, 2, 0),
    ("What's 15 multiplied by 8?", 2, 2, 0),
    ("Name the planets in our solar system.", 2, 2, 1),
    ("What are the primary colors?", 2, 2, 1),
    ("Who wrote 'Romeo and Juliet'?", 2, 2, 0),
    ("What's the chemical symbol for gold?", 2, 2, 0),
    ("How many bones are in the human body?", 2, 2, 0),
    ("What are the four cardinal directions?", 2, 2, 1),
    ("What's the square root of 144?", 2, 2, 0),
    
    # Complex Preferences and Habits
    ("Remember I prefer tea over coffee.", 0, 1, 0),
    ("Do I prefer tea or coffee?", 1, 1, 0),
    ("Store that I exercise every Tuesday and Thursday.", 0, 1, 0),
    ("When do I usually exercise?", 1, 1, 1),
    ("Note that I'm vegetarian.", 0, 1, 0),
    ("What dietary restrictions do I have?", 1, 1, 1),
    ("Remember I hate horror movies.", 0, 1, 0),
    ("What movie genres do I dislike?", 1, 1, 1),
    ("Save that my favorite cuisine is Italian.", 0, 1, 0),
    ("What's my favorite type of food?", 1, 1, 0),
    
    # Technology and Passwords
    ("Store my laptop password: SecurePass123.", 0, 1, 0),
    ("What's my laptop password?", 1, 1, 0),
    ("Remember my Amazon account: user@email.com.", 0, 1, 0),
    ("What's my Amazon login?", 1, 1, 0),
    ("Save my router IP address: 192.168.1.1.", 0, 1, 0),
    ("What's my router IP?", 1, 1, 0),
    ("Note my smartphone model: iPhone 15 Pro.", 0, 1, 0),
    ("What phone do I use?", 1, 1, 0),
    ("Remember my cloud storage has 2TB.", 0, 1, 0),
    ("How much cloud storage do I have?", 1, 1, 0),
    
    # Educational Information
    ("Store that I graduated from MIT in 2015.", 0, 1, 0),
    ("Where did I go to college?", 1, 1, 0),
    ("Remember my degree is in Computer Science.", 0, 1, 0),
    ("What did I study in college?", 1, 1, 0),
    ("Save that I speak English, Spanish, and French.", 0, 1, 0),
    ("What languages do I speak?", 1, 1, 1),
    ("Note that I have a Master's degree.", 0, 1, 0),
    ("What educational qualifications do I have?", 1, 1, 1),
    ("Remember I was valedictorian.", 0, 1, 0),
    ("What academic achievements do I have?", 1, 1, 1),
    
    # Travel and Transportation
    ("Store my passport number: AB1234567.", 0, 1, 0),
    ("What's my passport number?", 1, 1, 0),
    ("Remember I have a driver's license in California.", 0, 1, 0),
    ("What driver's license do I have?", 1, 1, 0),
    ("Save that I've visited 15 countries.", 0, 1, 0),
    ("How many countries have I visited?", 1, 1, 0),
    ("Note that my car is a blue Honda Civic.", 0, 1, 0),
    ("What car do I drive?", 1, 1, 0),
    ("Remember my frequent flyer number: FF987654.", 0, 1, 0),
    ("What's my frequent flyer number?", 1, 1, 0),
    
    # Temporary Information (Short-term)
    ("Remember the delivery code is 4567.", 0, 0, 0),
    ("What's the delivery code?", 1, 0, 0),
    ("Note that the repair appointment is Thursday 2 PM.", 0, 0, 0),
    ("When is my repair appointment?", 1, 0, 0),
    ("Store the taxi number: 555-TAXI.", 0, 0, 0),
    ("What taxi number did I save?", 1, 0, 0),
    ("Remember I borrowed John's charger.", 0, 0, 0),
    ("Whose charger did I borrow?", 1, 0, 0),
    ("Note that the conference room is B-204.", 0, 0, 0),
    ("Which conference room am I using?", 1, 0, 0),
    
    # Scientific Knowledge (Current)
    ("What's the speed of light?", 2, 2, 0),
    ("Name the noble gases.", 2, 2, 1),
    ("What's Newton's first law of motion?", 2, 2, 0),
    ("List the types of electromagnetic radiation.", 2, 2, 1),
    ("What's the atomic number of carbon?", 2, 2, 0),
    ("Explain photosynthesis.", 2, 2, 0),
    ("What are the phases of mitosis?", 2, 2, 1),
    ("What's the formula for water?", 2, 2, 0),
    ("Name the layers of Earth's atmosphere.", 2, 2, 1),
    ("What's absolute zero in Celsius?", 2, 2, 0),
    
    # Historical Facts (Current)
    ("When did World War II end?", 2, 2, 0),
    ("Who was the first person on the moon?", 2, 2, 0),
    ("What year was the Declaration of Independence signed?", 2, 2, 0),
    ("Name the ancient wonders of the world.", 2, 2, 1),
    ("When did the Berlin Wall fall?", 2, 2, 0),
    ("Who invented the telephone?", 2, 2, 0),
    ("What were the causes of World War I?", 2, 2, 1),
    ("When was the printing press invented?", 2, 2, 0),
    ("Who painted the Mona Lisa?", 2, 2, 0),
    ("What was the Renaissance period?", 2, 2, 0),
    
    # Sports and Hobbies
    ("Remember I play tennis every Saturday.", 0, 1, 0),
    ("What sports do I play?", 1, 1, 1),
    ("Store that my favorite team is the Lakers.", 0, 1, 0),
    ("What's my favorite sports team?", 1, 1, 0),
    ("Note that I collect vintage coins.", 0, 1, 0),
    ("What do I collect?", 1, 1, 1),
    ("Remember I play guitar and piano.", 0, 1, 0),
    ("What instruments do I play?", 1, 1, 1),
    ("Save that I run marathons.", 0, 1, 0),
    ("What running events do I participate in?", 1, 1, 1),
    
    # Family Information
    ("Remember I have two brothers and one sister.", 0, 1, 0),
    ("How many siblings do I have?", 1, 1, 0),
    ("Store that my mother's name is Maria.", 0, 1, 0),
    ("What's my mother's name?", 1, 1, 0),
    ("Note that my father is retired.", 0, 1, 0),
    ("What does my father do?", 1, 1, 0),
    ("Remember my daughter goes to Stanford.", 0, 1, 0),
    ("Where does my daughter go to school?", 1, 1, 0),
    ("Save that my son is 16 years old.", 0, 1, 0),
    ("How old is my son?", 1, 1, 0),
    
    # Entertainment Preferences
    ("Remember my favorite book is '1984'.", 0, 1, 0),
    ("What's my favorite book?", 1, 1, 0),
    ("Store that I love science fiction movies.", 0, 1, 0),
    ("What movie genres do I like?", 1, 1, 1),
    ("Note that my favorite band is The Beatles.", 0, 1, 0),
    ("What's my favorite music group?", 1, 1, 0),
    ("Remember I enjoy cooking shows.", 0, 1, 0),
    ("What TV shows do I like?", 1, 1, 1),
    ("Save that I play video games on weekends.", 0, 1, 0),
    ("When do I play video games?", 1, 1, 0),
    
    # Daily Routine Temporary Info
    ("Remember I have yoga class at 7 AM tomorrow.", 0, 0, 0),
    ("What do I have at 7 AM tomorrow?", 1, 0, 0),
    ("Note that I'm meeting Sarah for lunch today.", 0, 0, 0),
    ("Who am I having lunch with today?", 1, 0, 0),
    ("Store that the plumber is coming at 10 AM.", 0, 0, 0),
    ("When is the plumber coming?", 1, 0, 0),
    ("Remember I need to buy milk and bread.", 0, 0, 0),
    ("What do I need to buy?", 1, 0, 1),
    ("Note that my dentist appointment is next Tuesday.", 0, 0, 0),
    ("When is my dentist appointment?", 1, 0, 0),
    
    # Geography and Locations (Current)
    ("What's the highest mountain in the world?", 2, 2, 0),
    ("Name the Great Lakes.", 2, 2, 1),
    ("What's the longest river in the world?", 2, 2, 0),
    ("Which countries border Mexico?", 2, 2, 1),
    ("What's the smallest country in the world?", 2, 2, 0),
    ("Name the continents.", 2, 2, 1),
    ("What's the deepest ocean trench?", 2, 2, 0),
    ("Which desert is the largest in the world?", 2, 2, 0),
    ("What are the time zones in the US?", 2, 2, 1),
    ("Name the Nordic countries.", 2, 2, 1),
    
    # Mathematical Operations (Current)
    ("What's 127 plus 384?", 2, 2, 0),
    ("Calculate 25% of 400.", 2, 2, 0),
    ("What's the area of a circle with radius 5?", 2, 2, 0),
    ("Solve for x: 2x + 5 = 15.", 2, 2, 0),
    ("What's 12 factorial?", 2, 2, 0),
    ("Convert 100 Fahrenheit to Celsius.", 2, 2, 0),
    ("What's the Pythagorean theorem?", 2, 2, 0),
    ("Calculate the volume of a cube with side 4.", 2, 2, 0),
    ("What's the derivative of x²?", 2, 2, 0),
    ("Find the LCM of 12 and 18.", 2, 2, 0),
    
    # Health and Fitness Info
    ("Remember my target weight is 165 lbs.", 0, 1, 0),
    ("What's my target weight?", 1, 1, 0),
    ("Store that I'm lactose intolerant.", 0, 1, 0),
    ("What food intolerances do I have?", 1, 1, 1),
    ("Note that I sleep 7 hours per night.", 0, 1, 0),
    ("How many hours do I sleep?", 1, 1, 0),
    ("Remember I take vitamins C and D.", 0, 1, 0),
    ("What vitamins do I take?", 1, 1, 1),
    ("Save that my resting heart rate is 65 bpm.", 0, 1, 0),
    ("What's my resting heart rate?", 1, 1, 0),
    
    # Programming and Technical Knowledge (Current)
    ("What does HTML stand for?", 2, 2, 0),
    ("Explain what a for loop does.", 2, 2, 0),
    ("What are the basic data types in Python?", 2, 2, 1),
    ("What's the difference between HTTP and HTTPS?", 2, 2, 0),
    ("What is machine learning?", 2, 2, 0),
    ("Explain object-oriented programming.", 2, 2, 0),
    ("What are the SOLID principles?", 2, 2, 1),
    ("What's a database index?", 2, 2, 0),
    ("Explain what APIs are used for.", 2, 2, 1),
    ("What's the difference between SQL and NoSQL?", 2, 2, 1),
    
    # Vehicle and License Information
    ("Store my license plate number: ABC-1234.", 0, 1, 0),
    ("What's my license plate number?", 1, 1, 0),
    ("Remember my car insurance expires in June.", 0, 1, 0),
    ("When does my car insurance expire?", 1, 1, 0),
    ("Note that my car has 85,000 miles.", 0, 1, 0),
    ("How many miles does my car have?", 1, 1, 0),
    ("Save my VIN number: 1HGBH41JXMN109186.", 0, 1, 0),
    ("What's my car's VIN number?", 1, 1, 0),
    ("Remember my motorcycle is a Harley Davidson.", 0, 1, 0),
    ("What motorcycle do I own?", 1, 1, 0),
    
    # Cultural Knowledge (Current)
    ("What are the five pillars of Islam?", 2, 2, 1),
    ("Name the Hindu festivals.", 2, 2, 1),
    ("What's the Jewish New Year called?", 2, 2, 0),
    ("When is Chinese New Year?", 2, 2, 0),
    ("What are the Four Noble Truths?", 2, 2, 1),
    ("Name traditional Japanese arts.", 2, 2, 1),
    ("What's the significance of Diwali?", 2, 2, 0),
    ("Explain the concept of karma.", 2, 2, 0),
    ("What are the Ten Commandments?", 2, 2, 1),
    ("Name famous Greek gods.", 2, 2, 1),
    
    # Shopping and Consumer Info
    ("Remember I shop at Whole Foods weekly.", 0, 1, 0),
    ("Where do I usually shop for groceries?", 1, 1, 0),
    ("Store my Amazon Prime membership expires in March.", 0, 1, 0),
    ("When does my Amazon Prime expire?", 1, 1, 0),
    ("Note that I prefer organic products.", 0, 1, 0),
    ("What kind of products do I prefer?", 1, 1, 1),
    ("Remember my clothing size is medium.", 0, 1, 0),
    ("What's my clothing size?", 1, 1, 0),
    ("Save that I have a Costco membership.", 0, 1, 0),
    ("What store memberships do I have?", 1, 1, 1),
    
    # Temporary Meeting/Event Info
    ("Remember the client meeting is in conference room A.", 0, 0, 0),
    ("Where is my client meeting?", 1, 0, 0),
    ("Note that the password for today's webinar is MEET2024.", 0, 0, 0),
    ("What's the webinar password?", 1, 0, 0),
    ("Store that I'm presenting slides 5-10.", 0, 0, 0),
    ("Which slides am I presenting?", 1, 0, 0),
    ("Remember the guest speaker arrives at 2 PM.", 0, 0, 0),
    ("When does the guest speaker arrive?", 1, 0, 0),
    ("Note that the catering is vegetarian.", 0, 0, 0),
    ("What type of catering did we order?", 1, 0, 0),
    
    # Literature and Arts (Current)
    ("Who wrote 'Pride and Prejudice'?", 2, 2, 0),
    ("What's a haiku?", 2, 2, 0),
    ("Name Shakespeare's tragedies.", 2, 2, 1),
    ("Who painted 'Starry Night'?", 2, 2, 0),
    ("What are the colors on the rainbow?", 2, 2, 1),
    ("What's the difference between poetry and prose?", 2, 2, 1),
    ("Who composed 'The Four Seasons'?", 2, 2, 0),
    ("What art movement was Picasso associated with?", 2, 2, 1),
    ("Name famous Renaissance artists.", 2, 2, 1),
    ("What's an allegory in literature?", 2, 2, 0),
    
    # Personal Goals and Aspirations
    ("Remember my goal is to learn Spanish this year.", 0, 1, 0),
    ("What language am I learning?", 1, 1, 0),
    ("Store that I want to run a marathon next year.", 0, 1, 0),
    ("What's my fitness goal?", 1, 1, 0),
    ("Note that I'm saving for a house down payment.", 0, 1, 0),
    ("What am I saving money for?", 1, 1, 0),
    ("Remember I want to visit Japan next spring.", 0, 1, 0),
    ("Where do I want to travel next?", 1, 1, 0),
    ("Save that my career goal is to become a manager.", 0, 1, 0),
    ("What's my career goal?", 1, 1, 0),
    
    # Pet and Animal Information
    ("Remember I have a golden retriever named Max.", 0, 1, 0),
    ("What pet do I have?", 1, 1, 0),
    ("Store that Max is 3 years old.", 0, 1, 0),
    ("How old is my dog?", 1, 1, 0),
    ("Note that my cat is allergic to chicken.", 0, 1, 0),
    ("What is my cat allergic to?", 1, 1, 1),
    ("Remember my veterinarian is Dr. Johnson.", 0, 1, 0),
    ("Who is my pet's veterinarian?", 1, 1, 0),
    ("Save that I feed my pets twice daily.", 0, 1, 0),
    ("How often do I feed my pets?", 1, 1, 0),
    
    # Weather and Climate (Current - no storage needed)
    ("What's the current temperature?", 2, 2, 0),
    ("Will it rain tomorrow?", 2, 2, 0),
    ("What's the weather forecast for this weekend?", 2, 2, 1),
    ("What's the humidity level today?", 2, 2, 0),
    ("When is sunset today?", 2, 2, 0),
    ("What's the UV index right now?", 2, 2, 0),
    ("Is there a storm warning?", 2, 2, 0),
    ("What's the wind speed?", 2, 2, 0),
    ("What's the air quality index?", 2, 2, 0),
    ("When will the snow start?", 2, 2, 0),
    
    # Recipe and Cooking Preferences
    ("Remember I'm allergic to shellfish.", 0, 1, 0),
    ("What food allergies do I have?", 1, 1, 1),
    ("Store that I prefer spicy food.", 0, 1, 0),
    ("What's my spice preference?", 1, 1, 0),
    ("Note that I don't eat red meat.", 0, 1, 0),
    ("What meats do I avoid?", 1, 1, 1),
    ("Remember my favorite dessert is chocolate cake.", 0, 1, 0),
    ("What's my favorite dessert?", 1, 1, 0),
    ("Save that I meal prep on Sundays.", 0, 1, 0),
    ("When do I meal prep?", 1, 1, 0),
    
    # Business and Economics (Current)
    ("What's the current stock market trend?", 2, 2, 0),
    ("Explain what GDP means.", 2, 2, 0),
    ("What are the types of business structures?", 2, 2, 1),
    ("What's the difference between stocks and bonds?", 2, 2, 1),
    ("What is compound interest?", 2, 2, 0),
    ("Explain supply and demand.", 2, 2, 0),
    ("What are the components of a business plan?", 2, 2, 1),
    ("What's market capitalization?", 2, 2, 0),
    ("Define return on investment.", 2, 2, 0),
    ("What are the different types of taxes?", 2, 2, 1),
    
    # Subscription and Service Information
    ("Remember my Netflix subscription expires in December.", 0, 1, 0),
    ("When does my Netflix subscription expire?", 1, 1, 0),
    ("Store that I have Spotify Premium.", 0, 1, 0),
    ("What music streaming service do I use?", 1, 1, 0),
    ("Note that my gym membership is $50/month.", 0, 1, 0),
    ("How much is my gym membership?", 1, 1, 0),
    ("Remember I subscribe to The New York Times.", 0, 1, 0),
    ("What newspaper do I subscribe to?", 1, 1, 0),
    ("Save that my cloud storage is with Google Drive.", 0, 1, 0),
    ("What cloud storage service do I use?", 1, 1, 0),
    
    # Emergency and Important Contacts
    ("Store my emergency contact: Jane Doe, 555-0199.", 0, 1, 0),
    ("Who is my emergency contact?", 1, 1, 0),
    ("Remember my doctor's emergency number: 555-URGENT.", 0, 1, 0),
    ("What's my doctor's emergency number?", 1, 1, 0),
    ("Note that my neighbor's name is Tom Wilson.", 0, 1, 0),
    ("What's my neighbor's name?", 1, 1, 0),
    ("Save my lawyer's contact: Attorney Smith, 555-LAW1.", 0, 1, 0),
    ("What's my lawyer's contact information?", 1, 1, 0),
    ("Remember my insurance agent is Mike Johnson.", 0, 1, 0),
    ("Who is my insurance agent?", 1, 1, 0),
    
    # Temporary Task and To-Do Items
    ("Remember I need to call the bank tomorrow.", 0, 0, 0),
    ("What do I need to do tomorrow?", 1, 0, 1),
    ("Note that I should pick up dry cleaning after work.", 0, 0, 0),
    ("What should I pick up after work?", 1, 0, 0),
    ("Store that I need to submit the report by Friday.", 0, 0, 0),
    ("When is my report due?", 1, 0, 0),
    ("Remember to water the plants this evening.", 0, 0, 0),
    ("What should I do this evening?", 1, 0, 1),
    ("Note that I need to renew my passport soon.", 0, 0, 0),
    ("What document do I need to renew?", 1, 0, 0),
    
    # Music and Entertainment Preferences
    ("Remember I enjoy jazz music.", 0, 1, 0),
    ("What type of music do I like?", 1, 1, 1),
    ("Store that my favorite album is 'Dark Side of the Moon'.", 0, 1, 0),
    ("What's my favorite album?", 1, 1, 0),
    ("Note that I play chess on weekends.", 0, 1, 0),
    ("What games do I play?", 1, 1, 1),
    ("Remember I'm learning to play the violin.", 0, 1, 0),
    ("What instrument am I learning?", 1, 1, 0),
    ("Save that I attend concerts regularly.", 0, 1, 0),
    ("How often do I attend concerts?", 1, 1, 0),
    
    # Philosophy and Religion (Current Knowledge)
    ("What is existentialism?", 2, 2, 0),
    ("Explain the concept of free will.", 2, 2, 0),
    ("What are the main world religions?", 2, 2, 1),
    ("Who was Socrates?", 2, 2, 0),
    ("What is the meaning of life according to philosophy?", 2, 2, 1),
    ("Explain Plato's cave allegory.", 2, 2, 0),
    ("What is Buddhism's Eightfold Path?", 2, 2, 1),
    ("Who wrote 'Thus Spoke Zarathustra'?", 2, 2, 0),
    ("What is moral relativism?", 2, 2, 0),
    ("Explain the concept of karma in Hinduism.", 2, 2, 0),
    
    # Social Media and Online Presence
    ("Remember my Twitter handle is @johndoe123.", 0, 1, 0),
    ("What's my Twitter handle?", 1, 1, 0),
    ("Store that I have 500 Instagram followers.", 0, 1, 0),
    ("How many Instagram followers do I have?", 1, 1, 0),
    ("Note that I post on LinkedIn weekly.", 0, 1, 0),
    ("How often do I post on LinkedIn?", 1, 1, 0),
    ("Remember my YouTube channel has 1000 subscribers.", 0, 1, 0),
    ("How many YouTube subscribers do I have?", 1, 1, 0),
    ("Save that I'm active on Reddit daily.", 0, 1, 0),
    ("How often am I on Reddit?", 1, 1, 0),
    
    # Clothing and Fashion Preferences
    ("Remember I prefer casual clothing.", 0, 1, 0),
    ("What's my clothing style preference?", 1, 1, 0),
    ("Store that my shoe size is 10.5.", 0, 1, 0),
    ("What's my shoe size?", 1, 1, 0),
    ("Note that I don't like wearing ties.", 0, 1, 0),
    ("What clothing items do I dislike?", 1, 1, 1),
    ("Remember my favorite color for clothes is blue.", 0, 1, 0),
    ("What's my favorite clothing color?", 1, 1, 0),
    ("Save that I shop for clothes twice a year.", 0, 1, 0),
    ("How often do I shop for clothes?", 1, 1, 0),
    
    # Temporary Event Information
    ("Remember the wedding is this Saturday at 3 PM.", 0, 0, 0),
    ("When is the wedding?", 1, 0, 0),
    ("Note that I'm bringing potato salad to the potluck.", 0, 0, 0),
    ("What am I bringing to the potluck?", 1, 0, 0),
    ("Store that the concert tickets are in my email.", 0, 0, 0),
    ("Where are my concert tickets?", 1, 0, 0),
    ("Remember the birthday party theme is '80s.", 0, 0, 0),
    ("What's the birthday party theme?", 1, 0, 0),
    ("Note that the reunion is at the Hilton Hotel.", 0, 0, 0),
    ("Where is the reunion being held?", 1, 0, 0),
    
    # Gaming and Technology Interests
    ("Remember I play World of Warcraft.", 0, 1, 0),
    ("What online games do I play?", 1, 1, 1),
    ("Store that my gaming PC has 32GB RAM.", 0, 1, 0),
    ("How much RAM does my gaming PC have?", 1, 1, 0),
    ("Note that I prefer PlayStation over Xbox.", 0, 1, 0),
    ("Which gaming console do I prefer?", 1, 1, 0),
    ("Remember my Steam library has 200+ games.", 0, 1, 0),
    ("How many Steam games do I own?", 1, 1, 0),
    ("Save that I stream on Twitch occasionally.", 0, 1, 0),
    ("Do I stream online?", 1, 1, 0),
    
    # Seasonal and Holiday Preferences
    ("Remember my favorite season is autumn.", 0, 1, 0),
    ("What's my favorite season?", 1, 1, 0),
    ("Store that I celebrate Christmas and Easter.", 0, 1, 0),
    ("What holidays do I celebrate?", 1, 1, 1),
    ("Note that I go skiing every winter.", 0, 1, 0),
    ("What winter activity do I do?", 1, 1, 0),
    ("Remember I host Thanksgiving dinner annually.", 0, 1, 0),
    ("What holiday do I host?", 1, 1, 0),
    ("Save that I take summer vacation in July.", 0, 1, 0),
    ("When do I take summer vacation?", 1, 1, 0),
    
    # Biology and Nature Knowledge (Current)
    ("What's the largest mammal on Earth?", 2, 2, 0),
    ("Name the types of ecosystems.", 2, 2, 1),
    ("How many chambers does a human heart have?", 2, 2, 0),
    ("What process do plants use to make food?", 2, 2, 0),
    ("Name the different types of clouds.", 2, 2, 1),
    ("What's the gestation period of an elephant?", 2, 2, 0),
    ("Explain what DNA stands for.", 2, 2, 0),
    ("What are the main types of rocks?", 2, 2, 1),
    ("How do birds navigate during migration?", 2, 2, 1),
    ("What's the fastest land animal?", 2, 2, 0),
    
    # Banking and Financial Services
    ("Remember my bank is Chase Manhattan.", 0, 1, 0),
    ("Which bank do I use?", 1, 1, 0),
    ("Store that my checking account has $5,000.", 0, 1, 0),
    ("How much is in my checking account?", 1, 1, 0),
    ("Note that I have automatic bill pay set up.", 0, 1, 0),
    ("Do I have automatic bill pay?", 1, 1, 0),
    ("Remember my credit card limit is $10,000.", 0, 1, 0),
    ("What's my credit card limit?", 1, 1, 0),
    ("Save that I contribute $500/month to 401k.", 0, 1, 0),
    ("How much do I contribute to my 401k?", 1, 1, 0),
    
    # Immediate Daily Tasks (Short-term)
    ("Remember I have a haircut appointment at 2 PM.", 0, 0, 0),
    ("When is my haircut appointment?", 1, 0, 0),
    ("Note that I need to call mom tonight.", 0, 0, 0),
    ("Who do I need to call tonight?", 1, 0, 0),
    ("Store that I'm having dinner with friends at 7 PM.", 0, 0, 0),
    ("What time is dinner with friends?", 1, 0, 0),
    ("Remember the grocery list: milk, eggs, bread, cheese.", 0, 0, 0),
    ("What's on my grocery list?", 1, 0, 1),
    ("Note that I need to charge my phone before leaving.", 0, 0, 0),
    ("What do I need to do before leaving?", 1, 0, 0),
    
    # Space and Astronomy (Current)
    ("How many moons does Jupiter have?", 2, 2, 0),
    ("What's the closest star to Earth?", 2, 2, 0),
    ("Name the phases of the moon.", 2, 2, 1),
    ("What's a black hole?", 2, 2, 0),
    ("How long does it take Earth to orbit the Sun?", 2, 2, 0),
    ("What's the Milky Way galaxy?", 2, 2, 0),
    ("Name the planets in order from the Sun.", 2, 2, 1),
    ("What's the difference between a meteor and meteorite?", 2, 2, 1),
    ("How far is the Moon from Earth?", 2, 2, 0),
    ("What causes the seasons on Earth?", 2, 2, 0),
    
    # Cooking Skills and Kitchen Info
    ("Remember I know how to make pasta from scratch.", 0, 1, 0),
    ("What cooking skills do I have?", 1, 1, 1),
    ("Store that my kitchen has a gas stove.", 0, 1, 0),
    ("What type of stove do I have?", 1, 1, 0),
    ("Note that I own a stand mixer.", 0, 1, 0),
    ("What kitchen appliances do I own?", 1, 1, 1),
    ("Remember my signature dish is lasagna.", 0, 1, 0),
    ("What's my signature dish?", 1, 1, 0),
    ("Save that I grow herbs on my windowsill.", 0, 1, 0),
    ("What do I grow in my kitchen?", 1, 1, 1),
    
    # Language and Communication (Current)
    ("What are the Romance languages?", 2, 2, 1),
    ("How many letters are in the English alphabet?", 2, 2, 0),
    ("What's the most spoken language in the world?", 2, 2, 0),
    ("Explain what a palindrome is.", 2, 2, 0),
    ("What are the parts of speech?", 2, 2, 1),
    ("What's the difference between a simile and metaphor?", 2, 2, 1),
    ("How many words are in the average English vocabulary?", 2, 2, 0),
    ("What is sign language?", 2, 2, 0),
    ("Name some extinct languages.", 2, 2, 1),
    ("What's the origin of the word 'alphabet'?", 2, 2, 0),
    
    # Investment and Retirement Planning
    ("Remember I have a Roth IRA with Vanguard.", 0, 1, 0),
    ("Where is my Roth IRA?", 1, 1, 0),
    ("Store that I plan to retire at 65.", 0, 1, 0),
    ("When do I plan to retire?", 1, 1, 0),
    ("Note that I invest in index funds.", 0, 1, 0),
    ("What type of investments do I make?", 1, 1, 1),
    ("Remember my target retirement savings is $1 million.", 0, 1, 0),
    ("What's my retirement savings target?", 1, 1, 0),
    ("Save that I review my portfolio quarterly.", 0, 1, 0),
    ("How often do I review my investment portfolio?", 1, 1, 0),
    
    # Art and Creativity Hobbies
    ("Remember I paint watercolors on weekends.", 0, 1, 0),
    ("What art do I create?", 1, 1, 1),
    ("Store that I have an art studio in my garage.", 0, 1, 0),
    ("Where is my art studio?", 1, 1, 0),
    ("Note that I prefer abstract art.", 0, 1, 0),
    ("What art style do I prefer?", 1, 1, 0),
    ("Remember I take pottery classes monthly.", 0, 1, 0),
    ("What art classes do I take?", 1, 1, 1),
    ("Save that I display my art at local galleries.", 0, 1, 0),
    ("Where do I display my artwork?", 1, 1, 1),
    
    # Current Events and News (Immediate)
    ("What's the latest news today?", 2, 2, 1),
    ("What's the current stock market status?", 2, 2, 0),
    ("Are there any weather alerts in my area?", 2, 2, 1),
    ("What's trending on social media today?", 2, 2, 1),
    ("What are today's sports scores?", 2, 2, 1),
    ("Is there any breaking news right now?", 2, 2, 1),
    ("What's the current price of Bitcoin?", 2, 2, 0),
    ("Are there any traffic alerts for my commute?", 2, 2, 1),
    ("What movies are playing in theaters now?", 2, 2, 1),
    ("What's the current unemployment rate?", 2, 2, 0),
    
    # Photography and Equipment
    ("Remember I have a Canon DSLR camera.", 0, 1, 0),
    ("What camera do I own?", 1, 1, 0),
    ("Store that I specialize in landscape photography.", 0, 1, 0),
    ("What type of photography do I do?", 1, 1, 1),
    ("Note that I have a 50mm and 85mm lens.", 0, 1, 0),
    ("What camera lenses do I own?", 1, 1, 1),
    ("Remember I edit photos in Lightroom.", 0, 1, 0),
    ("What software do I use for photo editing?", 1, 1, 0),
    ("Save that I sell prints online.", 0, 1, 0),
    ("Do I sell my photography?", 1, 1, 0),
    
    # Garden and Plant Care
    ("Remember I have a vegetable garden.", 0, 1, 0),
    ("What type of garden do I have?", 1, 1, 0),
    ("Store that I grow tomatoes, peppers, and herbs.", 0, 1, 0),
    ("What do I grow in my garden?", 1, 1, 1),
    ("Note that I water my plants every other day.", 0, 1, 0),
    ("How often do I water my plants?", 1, 1, 0),
    ("Remember I compost kitchen scraps.", 0, 1, 0),
    ("Do I compost organic waste?", 1, 1, 0),
    ("Save that my garden is 10x20 feet.", 0, 1, 0),
    ("What size is my garden?", 1, 1, 0),
    
    # Psychology and Mental Health (Current)
    ("What are the stages of grief?", 2, 2, 1),
    ("Explain what cognitive behavioral therapy is.", 2, 2, 0),
    ("What's the difference between anxiety and depression?", 2, 2, 1),
    ("What is mindfulness meditation?", 2, 2, 0),
    ("How does stress affect the body?", 2, 2, 1),
    ("What are coping mechanisms?", 2, 2, 1),
    ("Explain what emotional intelligence means.", 2, 2, 0),
    ("What's the fight or flight response?", 2, 2, 0),
    ("What are the symptoms of burnout?", 2, 2, 1),
    ("How does sleep affect mental health?", 2, 2, 1),
    
    # Appointment and Schedule Management (Temporary)
    ("Remember my therapy appointment is Thursday at 4 PM.", 0, 0, 0),
    ("When is my therapy appointment?", 1, 0, 0),
    ("Note that the team meeting moved to Wednesday 10 AM.", 0, 0, 0),
    ("When is the team meeting?", 1, 0, 0),
    ("Store that I have back-to-back calls from 2-4 PM today.", 0, 0, 0),
    ("What do I have from 2-4 PM today?", 1, 0, 0),
    ("Remember the project deadline is next Friday.", 0, 0, 0),
    ("When is the project deadline?", 1, 0, 0),
    ("Note that I'm out of office next Monday.", 0, 0, 0),
    ("Am I working next Monday?", 1, 0, 0),
    
    # Environmental and Sustainability
    ("Remember I recycle and use renewable energy.", 0, 1, 0),
    ("What do I do for environmental sustainability?", 1, 1, 1),
    ("Store that I drive a hybrid vehicle.", 0, 1, 0),
    ("What type of vehicle do I drive?", 1, 1, 0),
    ("Note that I buy organic and local produce.", 0, 1, 0),
    ("What type of produce do I buy?", 1, 1, 1),
    ("Remember I use reusable bags and water bottles.", 0, 1, 0),
    ("What reusable items do I use?", 1, 1, 1),
    ("Save that I participate in Earth Day activities.", 0, 1, 0),
    ("What environmental activities do I participate in?", 1, 1, 1),
    
    # Emergency Preparedness
    ("Remember I have a first aid kit in my car.", 0, 1, 0),
    ("Where do I keep my first aid kit?", 1, 1, 0),
    ("Store that my emergency fund has $10,000.", 0, 1, 0),
    ("How much is in my emergency fund?", 1, 1, 0),
    ("Note that I know CPR and basic first aid.", 0, 1, 0),
    ("What emergency skills do I have?", 1, 1, 1),
    ("Remember my evacuation plan includes meeting at the school.", 0, 1, 0),
    ("Where is my emergency meeting point?", 1, 1, 0),
    ("Save that I have 3 days of water and food stored.", 0, 1, 0),
    ("How many days of emergency supplies do I have?", 1, 1, 0),
    
    # Chemistry Knowledge (Current)
    ("What's the periodic table?", 2, 2, 0),
    ("What are the noble gases?", 2, 2, 1),
    ("What's the molecular formula for carbon dioxide?", 2, 2, 0),
    ("Explain what acids and bases are.", 2, 2, 1),
    ("What's the difference between ionic and covalent bonds?", 2, 2, 1),
    ("What is pH and what does it measure?", 2, 2, 0),
    ("Name the states of matter.", 2, 2, 1),
    ("What's the atomic structure of an atom?", 2, 2, 1),
    ("What is photosynthesis chemically?", 2, 2, 0),
    ("What are enzymes and what do they do?", 2, 2, 1),
    
    # Home Maintenance and DIY
    ("Remember I can fix basic plumbing issues.", 0, 1, 0),
    ("What home repairs can I do myself?", 1, 1, 1),
    ("Store that I have a well-stocked toolbox.", 0, 1, 0),
    ("What tools do I have?", 1, 1, 1),
    ("Note that I painted my living room last year.", 0, 1, 0),
    ("What rooms have I painted recently?", 1, 1, 1),
    ("Remember my house was built in 1995.", 0, 1, 0),
    ("When was my house built?", 1, 1, 0),
    ("Save that I replace air filters every 3 months.", 0, 1, 0),
    ("How often do I replace air filters?", 1, 1, 0),
    
    # Networking and Professional Contacts
    ("Remember my mentor is Dr. Sarah Wilson.", 0, 1, 0),
    ("Who is my professional mentor?", 1, 1, 0),
    ("Store that I attend monthly networking events.", 0, 1, 0),
    ("How often do I attend networking events?", 1, 1, 0),
    ("Note that I'm a member of the Professional Engineers Society.", 0, 1, 0),
    ("What professional organizations am I a member of?", 1, 1, 1),
    ("Remember I have 500+ LinkedIn connections.", 0, 1, 0),
    ("How many LinkedIn connections do I have?", 1, 1, 0),
    ("Save that I volunteer at local tech meetups.", 0, 1, 0),
    ("Where do I volunteer professionally?", 1, 1, 1),
    
    # Physics Knowledge (Current)
    ("What are Newton's three laws of motion?", 2, 2, 1),
    ("What is the speed of sound?", 2, 2, 0),
    ("Explain what gravity is.", 2, 2, 0),
    ("What's the difference between mass and weight?", 2, 2, 1),
    ("What is electromagnetic radiation?", 2, 2, 0),
    ("How does a lever work?", 2, 2, 0),
    ("What are the different types of energy?", 2, 2, 1),
    ("Explain what quantum mechanics is.", 2, 2, 0),
    ("What's the relationship between energy and matter?", 2, 2, 0),
    ("What causes lightning and thunder?", 2, 2, 1),
    
    # Temporary Shopping and Errands
    ("Remember I need to buy a birthday gift for Mom.", 0, 0, 0),
    ("What do I need to buy for Mom?", 1, 0, 0),
    ("Note that I should pick up my prescription today.", 0, 0, 0),
    ("What should I pick up today?", 1, 0, 0),
    ("Store that I need batteries for the remote.", 0, 0, 0),
    ("What batteries do I need to buy?", 1, 0, 0),
    ("Remember the dry cleaning is ready for pickup.", 0, 0, 0),
    ("What's ready for pickup?", 1, 0, 0),
    ("Note that I should return the library books tomorrow.", 0, 0, 0),
    ("What should I return tomorrow?", 1, 0, 0),
    
    # Mixed and Complex Queries
    ("What are all my stored passwords?", 1, 1, 1),
    ("List everything I need to do this week.", 1, 0, 1),
    ("What personal information do you have about me?", 1, 1, 1),
    ("Tell me about my family members.", 1, 1, 1),
    ("What are my upcoming appointments?", 1, 0, 1),
    ("Summarize my health information.", 1, 1, 1),
    ("What goals and aspirations have I shared?", 1, 1, 1),
    ("List my subscriptions and memberships.", 1, 1, 1),
    ("What are my hobbies and interests?", 1, 1, 1),
    ("Tell me about my work and career information.", 1, 1, 1),
    
    # No Clear Answer Scenarios
    ("What should I have for breakfast?", 2, 2, 1),
    ("Should I call in sick tomorrow?", 2, 2, 1),
    ("What color should I paint my room?", 2, 2, 1),
    ("Should I invest in stocks or bonds?", 2, 2, 1),
    ("What career path should I choose?", 2, 2, 1),
    ("Should I adopt a pet?", 2, 2, 1),
    ("What hobby should I pick up?", 2, 2, 1),
    ("Should I move to a different city?", 2, 2, 1),
    ("What book should I read next?", 2, 2, 1),
    ("Should I take that job offer?", 2, 2, 1),
    
    # Edge Cases and Ambiguous Queries
    ("Remember something important.", 0, 2, 2),
    ("Tell me what I should know.", 1, 2, 1),
    ("Store this for later.", 0, 2, 2),
    ("What did I forget?", 1, 2, 1),
    ("Help me remember.", 0, 2, 2),
    ("What should I be doing right now?", 2, 2, 1),
    ("Do you know about my...?", 1, 2, 1),
    ("Save it.", 0, 2, 2),
    ("What was that thing?", 1, 2, 0),
    ("Tell me again.", 1, 2, 0),
    
    # More specific technology queries
    ("Remember my WiFi router brand is Netgear.", 0, 1, 0),
    ("What brand is my WiFi router?", 1, 1, 0),
    ("Store that my smart TV is a Samsung 55-inch.", 0, 1, 0),
    ("What smart TV do I own?", 1, 1, 0),
    ("Note that I use an iPhone 15 Pro Max.", 0, 1, 0),
    ("What smartphone do I use?", 1, 1, 0),
    
    # More food preferences
    ("Remember I can't eat gluten.", 0, 1, 0),
    ("What foods can't I eat?", 1, 1, 1),
    ("Store that I love Thai food.", 0, 1, 0),
    ("What's my favorite ethnic cuisine?", 1, 1, 0),
    
    # More immediate tasks
    ("Remember to submit my timesheet by 5 PM.", 0, 0, 0),
    ("What do I need to submit today?", 1, 0, 0),
    ("Note that I have a dental cleaning tomorrow at 9 AM.", 0, 0, 0),
    ("What appointment do I have tomorrow morning?", 1, 0, 0),
    
    # Complex retrieval scenarios
    ("What medical appointments do I have scheduled?", 1, 0, 1),
    ("List all my account passwords.", 1, 1, 1),
    ("What family birthdays are coming up?", 1, 1, 1),
    ("Tell me about my investment accounts.", 1, 1, 1),
    ("What home improvement projects have I mentioned?", 1, 1, 1),
    
    # More general knowledge
    ("How do solar panels work?", 2, 2, 0),
    ("What causes climate change?", 2, 2, 1),
    ("Explain blockchain technology.", 2, 2, 0),
    ("What is artificial intelligence?", 2, 2, 0),
    ("How does the internet work?", 2, 2, 1)
]





# from src.Brain.hippocampus import AnteriorCingulateCortex
# from src.Brain.one_many import MultiAnswerHeuristic
# from data import labeled_queries



# non_reasoning_model ="gemma3:4b"
# temperature = 0
# mem_in_out = AnteriorCingulateCortex(
#             model=non_reasoning_model,
#             temperature=temperature,
#             prompt_path="./src/prompts/memory_prompts/mem_in_out.txt"
#         )

# single_multi = MultiAnswerHeuristic()


# # Twin AI Training Dataset
# # attention_labels = ["memory_in", "memory_out", "cur"] (0, 1, 2)
# # memory_labels = ["STM", "LTM", "none"] (0, 1, 2) 
# # answer_labels = ["single", "multiple", "none"] (0, 1, 2)



# def label_data(query , type):
#     data = [query]
#     # Decide operation type
#     decision = mem_in_out.gateway_router(query)
#     if decision.get("operation") == "memory_in":
#         data.append(0)
#         data.append(type)
#         data.append(2)
#         return data
#     elif decision.get("operation") == "memory_out":
#         data.append(1)
#         data.append(type)  
#         if single_multi.expects_multiple_answers(query):
#             data.append(1)
#         else:
#             data.append(0)
#         return data

#     elif decision.get("operation") == "cur":
#         data.append(2)
#         data.append(2)
#         data.append(2)
#         return tuple(data)
    

# for data in labeled_queries:
#     query , type = data
#     tup_labled = labeled_queries(query , type)
#     dataset.append(tup_labled)


import json
# from src.Brain.hippocampus import AnteriorCingulateCortex
# from src.Brain.one_many import MultiAnswerHeuristic
# from data import labeled_queries  # list of (query, type)

# non_reasoning_model = "gemma3:4b"
# temperature = 0

# mem_in_out = AnteriorCingulateCortex(
#     model=non_reasoning_model,
#     temperature=temperature,
#     prompt_path="./src/prompts/memory_prompts/mem_in_out.txt"
# )

# single_multi = MultiAnswerHeuristic()

# # Label mappings
# # attention_labels = ["memory_in", "memory_out", "cur"] -> (0, 1, 2)
# # memory_labels    = ["STM", "LTM", "none"] -> (0, 1, 2) 
# # answer_labels    = ["single", "multiple", "none"] -> (0, 1, 2)


# def label_data(query, mem_type):
#     data = [query]

#     # Decide operation type
#     decision = mem_in_out.gateway_router(query)

#     if decision.get("operation") == "memory_in":
#         data.append(0)   # memory_in
#         data.append(mem_type)  # STM/LTM decided outside
#         data.append(2)   # no answer type for memory_in
#         return tuple(data)

#     elif decision.get("operation") == "memory_out":
#         data.append(1)   # memory_out
#         data.append(mem_type)  # STM/LTM decided outside

#         # single or multiple answers
#         if single_multi.expects_multiple_answers(query):
#             data.append(1)   # multiple
#         else:
#             data.append(0)   # single
#         return tuple(data)

#     elif decision.get("operation") == "cur":
#         data.append(2)   # cur
#         data.append(2)   # no memory type
#         data.append(2)   # no answer type
#         return tuple(data)

#     else:
#         return None


# # Generate dataset
# dataset = []
# for query, mem_type in labeled_queries:  # labeled_queries = [(query, mem_type), ...]
#     tup_labeled = label_data(query, mem_type)
#     if tup_labeled:
#         dataset.append(tup_labeled)

# # Save to file
# with open("labeled_dataset.json", "w", encoding="utf-8") as f:
#     json.dump(dataset, f, indent=2, ensure_ascii=False)

# print(f"✅ Saved {len(dataset)} labeled queries to labeled_dataset.json")



import json

# Path to your dataset file
file_path = "labeled_dataset.json"

# Example new data (list of tuples)
# new_data = [
#     ("How do solar panels work?", 2, 2, 0),
#     ("Remember my birthday is June 5th", 0, 0, 2),
#     ("What is my birthday?", 1, 0, 0),
# ]

# Convert tuples to lists (JSON doesn’t support tuples)
new_data_as_lists = [list(item) for item in new_data]

# Load existing dataset
try:
    with open(file_path, "r") as f:
        dataset = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    dataset = []

# Append new data
dataset.extend(new_data_as_lists)

# Save updated dataset
with open(file_path, "w") as f:
    json.dump(dataset, f, indent=4)

print(f"✅ Added {len(new_data)} items. Total dataset size: {len(dataset)}")
