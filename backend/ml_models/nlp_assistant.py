"""
Air Quality Platform - NLP AI Health Assistant Chatbot
Pluggable LLM interface with RAG for environmental health guidance.
"""

import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Knowledge base for RAG
KNOWLEDGE_BASE = {
    "aqi_explanation": {
        "keywords": ["aqi", "air quality index", "what is aqi", "explain aqi", "aqi meaning"],
        "response": """**Air Quality Index (AQI)** is a standardized indicator for reporting daily air quality. It tells you how clean or polluted the air is.

📊 **AQI Scale:**
| Range | Category | Health Impact |
|-------|----------|--------------|
| 0-50 | 🟢 Good | Minimal impact |
| 51-100 | 🟡 Moderate | Acceptable quality |
| 101-150 | 🟠 Unhealthy (Sensitive) | Sensitive groups affected |
| 151-200 | 🔴 Unhealthy | Everyone may feel effects |
| 201-300 | 🟣 Very Unhealthy | Health alert |
| 301-500 | 🟤 Hazardous | Emergency conditions |

The AQI is calculated using concentrations of PM2.5, PM10, CO, SO₂, NO₂, and O₃. The highest sub-index becomes the overall AQI."""
    },
    "masks": {
        "keywords": ["mask", "n95", "protection", "respiratory protection", "face mask"],
        "response": """**Mask Recommendations Based on AQI:**

🟢 **AQI 0-100:** No mask needed for most people.
🟡 **AQI 101-150:** N95 mask recommended for sensitive groups (children, elderly, asthmatics).
🔴 **AQI 151-200:** N95/KN95 mask recommended for everyone outdoors.
🟣 **AQI 201-300:** N95 mask essential. Limit outdoor exposure.
🟤 **AQI 300+:** N95 with exhalation valve. Avoid going outdoors.

**Mask Tips:**
- Ensure proper fit (no gaps around nose and chin)
- Replace N95 masks every 40 hours of use
- Children need child-sized masks
- Cloth masks do NOT filter fine particles (PM2.5)"""
    },
    "precautions": {
        "keywords": ["precaution", "protect", "safety", "what should i do", "how to stay safe", "tips"],
        "response": """**Air Pollution Safety Precautions:**

🏠 **Indoor Protection:**
- Keep windows and doors closed during high AQI
- Use HEPA air purifiers
- Avoid using candles, incense, or gas stoves
- Wet-mop floors to reduce settled particles

🚶 **Outdoor Protection:**
- Check AQI before going out
- Avoid heavy exercise when AQI > 100
- Wear N95 mask when AQI > 150
- Choose routes away from heavy traffic

👶 **Vulnerable Groups:**
- Children, elderly, and pregnant women should stay indoors when AQI > 150
- Keep rescue inhalers accessible
- Stay hydrated
- Monitor symptoms: coughing, wheezing, eye irritation"""
    },
    "symptoms": {
        "keywords": ["symptom", "health effect", "breathing", "cough", "wheeze", "asthma", "respiratory"],
        "response": """**Health Symptoms from Air Pollution:**

**Immediate Effects:**
- 😷 Coughing, sneezing, throat irritation
- 👁️ Eye burning, watering
- 🤧 Runny or stuffy nose
- 😮‍💨 Shortness of breath
- 🤕 Headache, dizziness

**When to Seek Medical Help:**
- Persistent difficulty breathing
- Chest pain or tightness
- Severe coughing with mucus
- Worsening asthma attacks
- Confusion or excessive fatigue

**At-Risk Groups:**
- People with asthma or COPD
- Heart disease patients
- Children under 5
- Adults over 65
- Pregnant women
- Outdoor workers"""
    },
    "emergency": {
        "keywords": ["emergency", "dangerous", "hazardous", "severe pollution", "what to do emergency"],
        "response": """🚨 **Emergency Air Quality Response:**

**If AQI exceeds 300 (Hazardous):**
1. **Stay indoors** — close all windows and doors
2. **Seal gaps** in windows/doors with wet towels
3. **Run air purifiers** on maximum setting
4. **Avoid all outdoor activity**
5. **Wear N95 mask** even indoors if needed
6. **Keep medications ready** (inhalers, heart meds)

**Emergency Numbers (India):**
- 🚑 Ambulance: 108
- 🏥 Health Helpline: 104
- ☎️ Emergency: 112

**If experiencing severe symptoms:**
- Call 108 immediately
- Do NOT drive — call for help
- Move to a well-ventilated area away from pollution source"""
    },
    "pollutants": {
        "keywords": ["pm2.5", "pm10", "pollutant", "carbon monoxide", "ozone", "nitrogen dioxide", "sulfur dioxide"],
        "response": """**Understanding Air Pollutants:**

**PM2.5 (Fine Particles)**
- Size: < 2.5 micrometers
- Sources: Vehicle exhaust, burning, industrial
- Danger: Penetrates deep into lungs and bloodstream

**PM10 (Coarse Particles)**
- Size: < 10 micrometers
- Sources: Dust, construction, pollen
- Danger: Affects upper respiratory tract

**CO (Carbon Monoxide)**
- Colorless, odorless gas
- Sources: Vehicle exhaust, incomplete combustion
- Danger: Reduces oxygen in blood

**NO₂ (Nitrogen Dioxide)**
- Reddish-brown gas
- Sources: Power plants, vehicles
- Danger: Inflames airways, worsens asthma

**SO₂ (Sulfur Dioxide)**
- Sources: Fossil fuel burning, industrial
- Danger: Causes breathing problems, acid rain

**O₃ (Ground-Level Ozone)**
- Formed by sunlight + pollutants
- Danger: Lung damage, chest pain"""
    },
}


class NLPAssistant:
    """
    AI Health Assistant chatbot with:
    - RAG (Retrieval-Augmented Generation) using environmental knowledge base
    - Pluggable LLM backend (OpenAI, Gemini, or simulated)
    - Context-aware health recommendations
    - Conversation history
    """

    def __init__(self, llm_provider: str = "simulated"):
        self.llm_provider = llm_provider
        self.conversation_history = []
        self.knowledge_base = KNOWLEDGE_BASE

    def chat(self, message: str, context: dict = None) -> dict:
        """
        Process a user message and return AI response.

        Args:
            message: User's question or message
            context: Optional context (current AQI, location, etc.)

        Returns:
            Response dict with answer, suggestions, and metadata
        """
        # Search knowledge base first (RAG)
        kb_response = self._search_knowledge_base(message)

        if kb_response:
            response = kb_response
        elif self.llm_provider == "simulated":
            response = self._simulated_response(message, context)
        else:
            response = self._llm_response(message, context)

        # Add context-aware additions
        if context and context.get("current_aqi"):
            aqi = context["current_aqi"]
            if aqi > 200:
                response += f"\n\n⚠️ **Current AQI is {aqi}** — This is unhealthy. Please take precautions."

        # Store conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat(),
        })

        # Generate follow-up suggestions
        suggestions = self._generate_suggestions(message)

        return {
            "response": response,
            "suggestions": suggestions,
            "context_used": bool(context),
            "source": "knowledge_base" if kb_response else self.llm_provider,
            "timestamp": datetime.now().isoformat(),
        }

    def _search_knowledge_base(self, message: str) -> str:
        """Search knowledge base for relevant information (RAG retrieval)."""
        message_lower = message.lower()

        best_match = None
        best_score = 0

        for topic, info in self.knowledge_base.items():
            keywords = info["keywords"]
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > best_score:
                best_score = score
                best_match = info["response"]

        return best_match if best_score > 0 else None

    def _simulated_response(self, message: str, context: dict = None) -> str:
        """Generate simulated AI response for demo mode."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["hello", "hi", "hey", "good"]):
            return ("👋 Hello! I'm your AI Air Quality Health Assistant. "
                    "I can help you with:\n\n"
                    "- 📊 Understanding AQI levels\n"
                    "- 😷 Mask recommendations\n"
                    "- 🏥 Health precautions\n"
                    "- 🚨 Emergency guidance\n"
                    "- 🌡️ Pollution explanations\n\n"
                    "What would you like to know?")

        if any(word in message_lower for word in ["forecast", "predict", "tomorrow", "next week"]):
            return ("📈 **AQI Forecast Analysis:**\n\n"
                    "Based on our LSTM + Prophet ensemble model:\n"
                    "- **Next 24h:** AQI expected to remain moderate (80-120)\n"
                    "- **3-day outlook:** Slight improvement expected due to wind patterns\n"
                    "- **7-day trend:** Gradual increase as temperatures rise\n\n"
                    "💡 *Tip: Check the Forecast page for detailed predictions with confidence intervals.*")

        if any(word in message_lower for word in ["exercise", "outdoor", "run", "walk", "jog"]):
            aqi = context.get("current_aqi", 100) if context else 100
            if aqi < 50:
                return "🏃 Great news! Air quality is **Good**. Perfect for outdoor exercise! Enjoy your workout."
            elif aqi < 100:
                return "🏃 Air quality is **Moderate**. Outdoor exercise is fine for most people. Sensitive individuals should monitor symptoms."
            elif aqi < 150:
                return "⚠️ Air quality is **Unhealthy for Sensitive Groups**. Consider indoor exercise or reduce outdoor workout intensity."
            else:
                return f"🚫 Current AQI is **{aqi}**. **Avoid outdoor exercise.** Use indoor gym or home workout instead. Wear N95 mask if you must go outside."

        if any(word in message_lower for word in ["thank", "thanks", "bye", "goodbye"]):
            return "😊 You're welcome! Stay safe and keep monitoring air quality. Feel free to ask anytime! 🌱"

        # Default response
        return ("I'd be happy to help with air quality and health information! "
                "Here are some topics I can assist with:\n\n"
                "1. 📊 **AQI Levels** — \"What is AQI?\"\n"
                "2. 😷 **Mask Advice** — \"Which mask should I use?\"\n"
                "3. 🛡️ **Precautions** — \"How to stay safe?\"\n"
                "4. 🏥 **Symptoms** — \"What are pollution symptoms?\"\n"
                "5. 🚨 **Emergency** — \"What to do in hazardous air?\"\n"
                "6. 🌡️ **Pollutants** — \"What is PM2.5?\"\n\n"
                "Just ask your question and I'll provide detailed guidance!")

    def _llm_response(self, message: str, context: dict = None) -> str:
        """Get response from external LLM (OpenAI/Gemini)."""
        try:
            if self.llm_provider == "openai":
                return self._openai_response(message, context)
            elif self.llm_provider == "gemini":
                return self._gemini_response(message, context)
        except Exception as e:
            logger.error(f"LLM API error: {e}")

        return self._simulated_response(message, context)

    def _openai_response(self, message: str, context: dict) -> str:
        """Call OpenAI API."""
        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        system_prompt = (
            "You are an expert AI health assistant specializing in air quality and environmental health. "
            "Provide accurate, helpful advice about air pollution, health risks, and safety precautions. "
            "Use emojis and formatting for readability. Be concise but thorough."
        )

        if context:
            system_prompt += f"\nCurrent context: AQI={context.get('current_aqi', 'N/A')}, "
            system_prompt += f"Location={context.get('location', 'N/A')}, "
            system_prompt += f"Temperature={context.get('temperature', 'N/A')}°C"

        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversation_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=800)
        return response.choices[0].message.content

    def _gemini_response(self, message: str, context: dict) -> str:
        """Call Gemini API."""
        # Placeholder for Gemini integration
        return self._simulated_response(message, context)

    def _generate_suggestions(self, message: str) -> list:
        """Generate follow-up question suggestions."""
        suggestions = [
            "What is the current AQI?",
            "Which mask should I use?",
            "Is it safe to exercise outdoors?",
            "What precautions should I take?",
            "Explain PM2.5 pollution",
            "What to do in emergency?",
        ]
        # Filter out suggestions similar to current message
        message_lower = message.lower()
        filtered = [s for s in suggestions if not any(w in message_lower for w in s.lower().split()[:3])]
        return random.sample(filtered, min(3, len(filtered)))

    def get_history(self) -> list:
        """Get conversation history."""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


# Singleton instance
nlp_assistant = NLPAssistant()
