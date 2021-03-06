import requests
import urllib
from bot_plugins import AbstractPlugin


class Recipe(AbstractPlugin.AbstractPlugin):
    API_URL = 'http://www.recipepuppy.com/api/?i={}&p=1'

    def get_help_message(self):
        return 'Type comma separated ingredients(meat,egg,potatoes)\n' \
               'and get list of links in response'

    def get_response(self, message):
        if self.validate_message(message):
            request_result = requests.get(self.build_url(message))
            result = self.format_output(request_result)
        else:
            result = self.get_help_message()
        return result

    def format_output(self, request_result):
        formatted_output = ''
        try:
            if not request_result.json()['results']:
                raise ValueError('Nothing found')

            for result_recipe in request_result.json()['results']:
                formatted_output += result_recipe['title'] + ' - '
                formatted_output += result_recipe['href']
                formatted_output += '\n'

        except ValueError:
            formatted_output += 'Nothing found for your ingredients :( Please try something else'
        return formatted_output

    def build_url(self, message):
        message = urllib.parse.quote(message.replace(' ', ''))
        url = self.API_URL.format(message)
        return url

    def validate_message(self, message):
        return True
