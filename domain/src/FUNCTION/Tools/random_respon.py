from random import choice

class RandomChoice:
    @staticmethod
    def random_choice(data:list) -> str:
        return choice(data)

# Usage Example:
# data_list = ["apple", "banana", "cherry", "date"]
# random_choice_instance = RandomChoice(data_list)
# random_item = random_choice_instance.random_choice()
# print(random_item)
