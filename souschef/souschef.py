class SousChef:
    def __init__(self, conversation_client, workspace_id, recipe_client):
        self.conversation_client = conversation_client
        self.recipe_client = recipe_client
        self.workspace_id = workspace_id

    @staticmethod
    def make_formatted_steps(recipe_info, recipe_steps):
        response = ["Ok, it takes " +
                    str(recipe_info['readyInMinutes']) +
                    " minutes to make " +
                    str(recipe_info['servings']) +
                    " servings of " +
                    recipe_info['title'] + ". Here are the steps:\n\n"]

        if recipe_steps and recipe_steps[0]['steps']:
            print str(recipe_steps[0]['steps'])
            for i, r_step in enumerate(recipe_steps[0]['steps']):
                equip_str = ""
                for e in r_step['equipment']:
                    equip_str += e['name'] + ", "
                if not equip_str:
                    equip_str = "None"
                else:
                    equip_str = equip_str[:-2]

                step = "Step " + str(i + 1) + ":\n" + \
                       "Equipment: " + equip_str + "\n" + \
                       "Action: " + r_step['step'] + "\n\n"

                step_breakdown = []
                for j in range(0, len(step), 300):
                    step_breakdown.append(step[j:min(len(step), j + 300)])

                for part in step_breakdown:
                    response.append(part)
        else:
            response.append("_No instructions available for this recipe._\n\n")

        response.append("Say anything to me to start over...")
        return response

    def handle_ingredients_message(self, message, context):
        if 'get_recipes' in context.keys() and \
                context['get_recipes']:
            context['recipes'] = \
                self.recipe_client.find_by_ingredients(message)

        response = "Lets see here...\n" + \
                   "I've found these recipes: \n"

        for i, recipe in enumerate(context['recipes']):
            response += str(i + 1) + ". " + recipe['title'] + "\n"
        response += "\nPlease enter the corresponding number of your choice."

        return response

    def handle_cuisine_message(self, cuisine, context):
        if 'get_recipes' in context.keys() and \
                context['get_recipes']:
            context['recipes'] = \
                self.recipe_client.find_by_cuisine(cuisine)

        response = "Lets see here...\n" + \
                   "I've found these recipes: \n"

        for i, recipe in enumerate(context['recipes']):
            response += str(i + 1) + ". " + recipe['title'] + "\n"
        response += "\nPlease enter the corresponding number of your choice."

        return response

    def handle_selection_message(self, selection, context):
        recipe_id = context['recipes'][selection - 1]['id']
        recipe_info = self.recipe_client.get_info_by_id(recipe_id)
        recipe_steps = self.recipe_client.get_steps_by_id(recipe_id)

        return self.make_formatted_steps(recipe_info, recipe_steps)

    def handle_message(self, message, context):
        print "Sending Watson context " + str(context)
        watson_response = self.conversation_client.message(
            workspace_id=self.workspace_id,
            message_input={'text': message},
            context=context)
        context = watson_response['context']
        print "Intent = " + watson_response['intents'][0]['intent']

        if 'is_ingredients' in context.keys() and context['is_ingredients']:
            response = self.handle_ingredients_message(message, context)

        elif 'is_selection' in context.keys() and context['is_selection']:
            context['selection_valid'] = False
            response = "Invalid selection! " + \
                       "Say anything to see your choices again..."

            if context['selection'].isdigit():
                selection = int(context['selection'])
                if 1 <= selection <= 5:
                    context['selection_valid'] = True
                    response = self.handle_selection_message(selection, context)

        elif watson_response['entities'] and watson_response['entities'][0]['entity'] == 'cuisine':
            cuisine = watson_response['entities'][0]['value']
            response = self.handle_cuisine_message(cuisine, context)

        else:
            response = ''
            for text in watson_response['output']['text']:
                response += text + "\n"

        return response, context
