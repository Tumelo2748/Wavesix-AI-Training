import streamlit as st
import openai
import json
import requests
from typing import Dict, List, Optional
import base64
from io import BytesIO
from PIL import Image
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="🥘 Visual Recipe Creator",
    page_icon="🥘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .recipe-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
    }
    
    .ingredient-card {
        background: #f8f9ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e1e5ff;
    }
    
    .step-number {
        background: #667eea;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    .hero-text {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class VisualRecipeCreator:
    def __init__(self):
        self.openai_client = None
        # Initialize OpenAI client with API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.setup_openai(api_key)
        
    def setup_openai(self, api_key: str):
        """Initialize OpenAI client"""
        openai.api_key = api_key
        self.openai_client = openai
        
    def parse_recipe(self, recipe_text: str) -> Dict:
        """Parse recipe text using GPT-4"""
        try:
            prompt = f"""
            Parse this recipe and return a structured JSON format with the following structure:
            {{
                "title": "Recipe Name",
                "description": "Brief description",
                "prep_time": "X minutes",
                "cook_time": "X minutes",
                "servings": "X servings",
                "difficulty": "Easy/Medium/Hard",
                "ingredients": [
                    {{"name": "ingredient name", "amount": "quantity", "unit": "measurement"}},
                ],
                "steps": [
                    {{"step_number": 1, "instruction": "detailed instruction", "time": "X minutes", "temperature": "X°F (if applicable)"}},
                ],
                "tips": ["helpful cooking tips"],
                "tags": ["cuisine type", "dietary restrictions", etc.]
            }}
            
            Recipe to parse:
            {recipe_text}
            
            Return only valid JSON, no additional text.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            parsed_recipe = json.loads(response.choices[0].message.content)
            return parsed_recipe
            
        except Exception as e:
            st.error(f"Error parsing recipe: {str(e)}")
            return None
    
    def generate_image(self, prompt: str, size: str = "512x512") -> Optional[str]:
        """Generate image using DALL-E"""
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=f"Professional food photography style: {prompt}. High quality, well-lit, appetizing presentation on clean background.",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            return response.data[0].url
            
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            return None
    
    def create_ingredient_images(self, ingredients: List[Dict]) -> Dict[str, str]:
        """Generate images for ingredients"""
        ingredient_images = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, ingredient in enumerate(ingredients):
            status_text.text(f"Generating image for {ingredient['name']}...")
            
            prompt = f"{ingredient['amount']} {ingredient['unit']} of {ingredient['name']}, ingredient photography"
            image_url = self.generate_image(prompt)
            
            if image_url:
                ingredient_images[ingredient['name']] = image_url
            
            progress_bar.progress((i + 1) / len(ingredients))
            time.sleep(1)  # Rate limiting
        
        status_text.text("Ingredient images generated!")
        return ingredient_images
    
    def create_step_images(self, steps: List[Dict], recipe_title: str) -> Dict[int, str]:
        """Generate images for cooking steps"""
        step_images = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, step in enumerate(steps):
            status_text.text(f"Generating image for step {step['step_number']}...")
            
            # Create a descriptive prompt for the cooking step
            prompt = f"Cooking step for {recipe_title}: {step['instruction'][:100]}... cooking process in kitchen"
            image_url = self.generate_image(prompt)
            
            if image_url:
                step_images[step['step_number']] = image_url
            
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(1)  # Rate limiting
        
        status_text.text("Step images generated!")
        return step_images

def main():
    # Header
    st.markdown("""
    <div class="hero-text">
        <h1>🥘 Visual Recipe Creator</h1>
        <p>Turn plain text recipes into beautiful, step-by-step visual guides with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize the app
    if 'recipe_creator' not in st.session_state:
        st.session_state.recipe_creator = VisualRecipeCreator()
      # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Check if API key is configured
        api_key_configured = st.session_state.recipe_creator.openai_client is not None
        
        if api_key_configured:
            st.success("✅ API Key configured from .env file!")
        else:
            st.error("❌ OpenAI API key not found in .env file")
            st.info("Please add your OpenAI API key to the .env file as OPENAI_API_KEY=your_key_here")
        
        st.markdown("---")
        
        # Options
        generate_ingredient_images = st.checkbox("Generate ingredient images", value=True, disabled=not api_key_configured)
        generate_step_images = st.checkbox("Generate step images", value=True, disabled=not api_key_configured)
        
        st.markdown("---")
        st.markdown("### 📋 Features")
        st.markdown("- 🧠 AI recipe parsing")
        st.markdown("- 🎨 Auto-generated images")
        st.markdown("- 📖 Visual step guides")
        st.markdown("- 💾 Export options")
      # Main content area
    if not st.session_state.recipe_creator.openai_client:
        st.warning("👈 Please configure your OpenAI API key in the .env file to get started!")
        st.info("""
        **How to configure the API key:**
        1. Go to [OpenAI Platform](https://platform.openai.com/)
        2. Sign up or log in to your account
        3. Navigate to API Keys section
        4. Create a new API key
        5. Add it to the .env file as: OPENAI_API_KEY=your_key_here
        6. Restart the application
        """)
        return
    
    # Recipe input
    st.header("📝 Enter Your Recipe")
    
    # Tabs for different input methods
    tab1, tab2 = st.tabs(["✍️ Paste Recipe", "📖 Example Recipe"])
    
    with tab1:
        recipe_input = st.text_area(
            "Paste your recipe here:",
            height=200,
            placeholder="Enter your recipe in any format - ingredients list, cooking instructions, etc."
        )
    
    with tab2:
        example_recipe = """
        Chocolate Chip Cookies
        
        Ingredients:
        - 2 1/4 cups all-purpose flour
        - 1 tsp baking soda
        - 1 tsp salt
        - 1 cup butter, softened
        - 3/4 cup granulated sugar
        - 3/4 cup brown sugar
        - 2 large eggs
        - 2 tsp vanilla extract
        - 2 cups chocolate chips
        
        Instructions:
        1. Preheat oven to 375°F
        2. Mix flour, baking soda, and salt in a bowl
        3. Cream butter and sugars until fluffy
        4. Beat in eggs and vanilla
        5. Gradually add flour mixture
        6. Stir in chocolate chips
        7. Drop spoonfuls on baking sheet
        8. Bake for 9-11 minutes until golden
        9. Cool on wire rack
        """
        
        if st.button("📋 Use Example Recipe"):
            recipe_input = example_recipe
            st.text_area("Example recipe loaded:", value=example_recipe, height=200, disabled=True)
    
    # Process recipe button
    if st.button("🚀 Create Visual Recipe", type="primary") and recipe_input:
        with st.spinner("🧠 Parsing recipe with AI..."):
            parsed_recipe = st.session_state.recipe_creator.parse_recipe(recipe_input)
        
        if parsed_recipe:
            # Display parsed recipe info
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="recipe-card">
                    <h2>{parsed_recipe.get('title', 'Delicious Recipe')}</h2>
                    <p>{parsed_recipe.get('description', 'A wonderful recipe to try!')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📊 Recipe Info")
                st.info(f"⏱️ Prep: {parsed_recipe.get('prep_time', 'N/A')}")
                st.info(f"🔥 Cook: {parsed_recipe.get('cook_time', 'N/A')}")
                st.info(f"👥 Serves: {parsed_recipe.get('servings', 'N/A')}")
                st.info(f"📈 Difficulty: {parsed_recipe.get('difficulty', 'N/A')}")
            
            # Generate images if requested
            ingredient_images = {}
            step_images = {}
            
            if generate_ingredient_images and parsed_recipe.get('ingredients'):
                st.header("🎨 Generating Ingredient Images...")
                ingredient_images = st.session_state.recipe_creator.create_ingredient_images(
                    parsed_recipe['ingredients']
                )
            
            if generate_step_images and parsed_recipe.get('steps'):
                st.header("🎨 Generating Step Images...")
                step_images = st.session_state.recipe_creator.create_step_images(
                    parsed_recipe['steps'], 
                    parsed_recipe.get('title', 'Recipe')
                )
            
            # Display ingredients with images
            st.header("🛒 Ingredients")
            
            ingredients_cols = st.columns(2)
            for i, ingredient in enumerate(parsed_recipe.get('ingredients', [])):
                with ingredients_cols[i % 2]:
                    st.markdown(f"""
                    <div class="ingredient-card">
                        <strong>{ingredient.get('amount', '')} {ingredient.get('unit', '')} {ingredient.get('name', '')}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if ingredient['name'] in ingredient_images:
                        st.image(ingredient_images[ingredient['name']], width=200)
            
            # Display cooking steps with images
            st.header("👨‍🍳 Cooking Steps")
            
            for step in parsed_recipe.get('steps', []):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="step-card">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <div class="step-number">{step.get('step_number', '')}</div>
                            <strong>Step {step.get('step_number', '')}</strong>
                        </div>
                        <p>{step.get('instruction', '')}</p>
                        {f"<small>⏱️ Time: {step.get('time', 'N/A')} | 🌡️ Temperature: {step.get('temperature', 'N/A')}</small>" if step.get('time') or step.get('temperature') else ""}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if step['step_number'] in step_images:
                        st.image(step_images[step['step_number']], width=250)
            
            # Display tips and tags
            if parsed_recipe.get('tips'):
                st.header("💡 Cooking Tips")
                for tip in parsed_recipe['tips']:
                    st.success(f"💡 {tip}")
            
            if parsed_recipe.get('tags'):
                st.header("🏷️ Tags")
                tags_html = " ".join([f"<span style='background: #667eea; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; margin: 0.2rem; display: inline-block;'>{tag}</span>" for tag in parsed_recipe['tags']])
                st.markdown(tags_html, unsafe_allow_html=True)
            
            # Export options
            st.header("💾 Export Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Download as JSON"):
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(parsed_recipe, indent=2),
                        file_name=f"{parsed_recipe.get('title', 'recipe').replace(' ', '_')}.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("🖨️ Print-Friendly View"):
                    st.info("Print-friendly view would open in a new tab (feature coming soon!)")
            
            with col3:
                if st.button("📱 Mobile View"):
                    st.info("Mobile-optimized view (feature coming soon!)")

if __name__ == "__main__":
    main()