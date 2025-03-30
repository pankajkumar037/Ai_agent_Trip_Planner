from crewai import Agent, Task, Crew


import os
from dotenv import load_dotenv
load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')


from crewai import LLM

llm = LLM(
    model="gemini/gemini-1.5-pro-latest",
    temperature=0.7,
    api_key=os.getenv('GOOGLE_API_KEY'),
)


class TripAgents:
    def __init__(self):
        self.llm = llm
        
    def city_selector_agent(self):
        return Agent(
            role='City Selection Expert',
            goal='Identify best cities to visit based on user preferences',
            backstory=(
                "An expert travel geographer with extensive knowledge about world cities "
                "and their cultural, historical, and entertainment offerings"
            ),
            llm=self.llm,
            verbose=True
        )
    
    def local_expert_agent(self):
        return Agent(
            role='Local Destination Expert',
            goal="Provide detailed insights about selected cities including top attractions, local customs, and hidden gems",
            backstory="A knowledgeable local guide with first-hand experience of the city's culture and attractions",
            llm=self.llm,
            verbose=True
        )
    
    def travel_planner_agent(self):
        return Agent(
            role='Professional Travel Planner',
            goal="Create detailed day-by-day itineraries with time allocations, transportation options, and activity sequencing",
            backstory="An experienced travel coordinator with perfect logistical planning skills",
            llm=self.llm,
            verbose=True
        )
    
    def budget_manager_agent(self):
        return Agent(
            role='Travel Budget Specialist',
            goal="Optimize travel plans to stay within budget while maximizing experience quality",
            backstory="A financial planner specializing in travel budgets and cost optimization",
            llm=self.llm,
            verbose=True
        )

class TripTasks:
    def __init__(self):
        pass
    
    def city_selection_task(self, agent, inputs):
        return Task(
            name="city_selection",  # Set task name for later extraction
            description=(
                f"Analyze user preferences and select best destinations:\n"
                f"- Travel Type: {inputs['travel_type']}\n"
                f"- Interests: {inputs['interests']}\n"
                f"- Season: {inputs['season']}\n"
                "Output: Provide 3 city options with a brief rationale for each."
            ),
            agent=agent,
            expected_output="Bullet-point list of 3 cities with 2-sentence explanations each."
        )
    
    def city_research_task(self, agent, city):
        return Task(
            name="city_research",  # Set task name
            description=(
                f"Provide detailed insights about {city} including:\n"
                "- Top 5 attractions\n"
                "- Local cuisine highlights\n"
                "- Cultural norms/etiquette\n"
                "- Recommended accommodation areas\n"
                "- Transportation tips"
            ),
            agent=agent,
            expected_output="Organized sections with clear headings and bullet points."
        )
    
    def itinerary_creation_task(self, agent, inputs, city):
        return Task(
            name="itinerary",  # Set task name
            description=(
                f"Create a {inputs['duration']}-day itinerary for {city} including:\n"
                "- Daily schedule with time allocations\n"
                "- Activity sequencing\n"
                "- Transportation between locations\n"
                "- Meal planning suggestions"
            ),
            agent=agent,
            expected_output="Day-by-day table format with time slots and activity details."
        )
    
    def budget_planning_task(self, agent, inputs, itinerary):
        return Task(
            name="budget",  # Set task name
            description=(
                f"Create a budget plan for the selected budget range ({inputs['budget']}) covering:\n"
                "- Accommodation costs\n"
                "- Transportation expenses\n"
                "- Activity fees\n"
                "- Meal budget\n"
                "- Emergency funds allocation"
            ),
            agent=agent,
            context=[itinerary],
            expected_output="Itemized budget table with total cost analysis."
        )

class TripCrew:
    def __init__(self, inputs,city):
        self.inputs = inputs
        self.city = city


    def run(self):
        agents = TripAgents()
        tasks = TripTasks()
        
        # Create Agents
        city_selector = agents.city_selector_agent()
        local_expert = agents.local_expert_agent()
        travel_planner = agents.travel_planner_agent()
        budget_manager = agents.budget_manager_agent()
        
        # Create Tasks with explicit names
        select_cities = tasks.city_selection_task(city_selector, self.inputs)
        research_city = tasks.city_research_task(local_expert, self.city)  
        create_itinerary = tasks.itinerary_creation_task(travel_planner, self.inputs, self.city)
        plan_budget = tasks.budget_planning_task(budget_manager, self.inputs, create_itinerary)
        
        # Assemble Crew and run all tasks
        crew = Crew(
            agents=[city_selector, local_expert, travel_planner, budget_manager],
            tasks=[select_cities, research_city, create_itinerary, plan_budget],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Use the tasks_output attribute (a list of TaskOutput objects) to build a dictionary.
        if hasattr(result, "tasks_output"):
            tasks_list = result.tasks_output
            final_result = {
                "city_selection": tasks_list[0].raw if len(tasks_list) > 0 else "❌ No city selection found.",
                "city_research": tasks_list[1].raw if len(tasks_list) > 1 else "❌ No city research found.",
                "itinerary": tasks_list[2].raw if len(tasks_list) > 2 else "❌ No itinerary generated.",
                "budget": tasks_list[3].raw if len(tasks_list) > 3 else "❌ No budget breakdown available."
            }
        else:
            final_result = {}
        
        # Log detailed raw outputs to the console (for debugging)
        print("Crew kickoff raw result:", result)
        if hasattr(result, "tasks_output"):
            for idx, task in enumerate(result.tasks_output):
                print(f"Task {idx} raw output:", task)
        
        return final_result
