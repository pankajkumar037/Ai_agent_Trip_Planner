import streamlit as st
from trip_agents import TripCrew
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def main():
    st.title("🤖 AI Travel Planning Assistant")
    
    # Sidebar for user inputs
    with st.sidebar:
        st.header("Trip Preferences")
        city=st.text_input("Enter city name")
        travel_type = st.selectbox("Travel Type", ["Leisure", "Business", "Adventure", "Cultural"])
        interests = st.multiselect("Interests", ["History", "Food", "Nature", "Art", "Shopping", "Nightlife"])
        season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Fall"])
        duration = st.slider("Trip Duration (days)", 1, 14, 7)
        budget = st.selectbox("Budget Range", ["$500-$1000", "$1000-$2000", "$2000-$5000", "Luxury"])
    
    # Button to generate the travel plan
    if st.button("Generate Travel Plan"):
        inputs = {
            "travel_type": travel_type,
            "interests": interests,
            "season": season,
            "duration": duration,
            "budget": budget
        }
        
        with st.spinner("🤖 AI Agents are working on your perfect trip..."):
            try:
                # Run the TripCrew and capture the result (a dictionary)
                crew_output = TripCrew(inputs,city).run()
                
                # Debugging: inspect the raw crew_output structure
                st.subheader("Debugging: Crew Output Data")
                st.write("Type of output:", type(crew_output))
                try:
                    st.json(crew_output)
                except Exception as ex:
                    st.write(crew_output)
                
                # Extract outputs using the keys from the returned dictionary
                city_selection = crew_output.get('city_selection', "❌ No city selection found.")
                city_research = crew_output.get('city_research', "❌ No city research found.")
                itinerary = crew_output.get('itinerary', "❌ No itinerary generated.")
                budget_breakdown = crew_output.get('budget', "❌ No budget breakdown available.")
                
                # Display results in expanders
                st.subheader("Your AI-Generated Travel Plan")
                with st.expander("Recommended Cities"):
                    st.markdown(city_selection)
                with st.expander("Destination Insights"):
                    st.markdown(city_research)
                with st.expander("Detailed Itinerary"):
                    st.markdown(itinerary)
                with st.expander("Budget Breakdown"):
                    st.markdown(budget_breakdown)
                
                st.success("✅ Trip planning completed! Enjoy your journey!")
            except Exception as e:
                st.error(f"An error occurred while processing the results: {e}")

if __name__ == "__main__":
    main()