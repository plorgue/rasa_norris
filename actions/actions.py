from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType
import requests


class AskForSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_joke_category"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        want_jokes = tracker.get_slot("want_jokes")
        if want_jokes:
            resp = requests.get(url="https://api.chucknorris.io/jokes/categories")
            if(resp.status_code == 200):
                categories = resp.json()
                category_string = "Themes available:"
                for category in categories:
                    category_string += ' ' + str(category) +','

                dispatcher.utter_message(text="What theme do you want?")
                dispatcher.utter_message(text=category_string[:-1])
            else:
                dispatcher.utter_message(text=resp.json())

        return []

class Displayjokes(Action):

    def name(self) -> Text:
        return "action_display_jokes"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        
        category = tracker.get_slot("joke_category")
        num = tracker.get_slot("num_jokes")
        want_jokes = tracker.get_slot("want_jokes")
        
        if want_jokes and num.isdigit() and len(category) > 3:
            count = 0
            for i in range(int(num)):
                resp = requests.get(url=f"https://api.chucknorris.io/jokes/random?category={category}")
                if(resp.status_code == 200):
                    joke = resp.json()['value']
                    dispatcher.utter_message(text=f"{i+1}. {joke}")
                else:
                    count += 1
            if count == int(num):
                dispatcher.utter_message(text=f"Sorry but I don't have funny jokes in the {category} theme. Try another :)")
            else: 
                dispatcher.utter_message(text="I know, I'm very funny")
        else:
            dispatcher.utter_message(text=f"Sorry but how is Chuck Norris? :'/")
        return []

class ValidateChuckNorrisForm(FormValidationAction):
    
    categories = []

    def __init__(self) -> None:
        super().__init__()
        resp = requests.get(url="https://api.chucknorris.io/jokes/categories")
        if(resp.status_code == 200):
            self.categories = resp.json()

    def name(self) -> Text:
        return "validate_chucknorris_form"

    def validate_want_jokes(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `want_jokes` value."""

        want = slot_value
        if want:
            return {"want_jokes": want}
        return {"want_jokes":  None}
        

    def validate_joke_category(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `joke_category` value."""

        # We need an available category.
        category = slot_value
        if category not in self.categories:
            dispatcher.utter_message(text="Please enter a valid theme :)")
            return {"joke_category": None}
        return {"joke_category": category}

    def validate_num_jokes(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `num_jokes` value."""

        # We want an integer.
        number = slot_value
        if number.isdigit() :
            return {"num_jokes": number}
        dispatcher.utter_message(text="Please enter a valid number")
        return {"num_jokes": None}


##################
# BORING ACTIONS #
################## 

def clean_name(name):
    return "".join([c for c in name if c.isalpha()])

class ValidateNameForm(FormValidationAction):


    def name(self) -> Text:
        return "validate_name_form"

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"first_name": None}
        return {"first_name": name}

    def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"last_name": None}
        
        first_name = tracker.get_slot("first_name")
        if len(first_name) + len(name) < 3:
            dispatcher.utter_message(text="That's a very short name. We fear a typo. Restarting!")
            return {"first_name": None, "last_name": None}
        return {"last_name": name}