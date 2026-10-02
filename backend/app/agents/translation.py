class TranslationAgent:
    """
    Independent Translation Agent module:
    Translates response summaries into English, Tamil, or Hindi.
    """
    TAMIL_MAP = {
        "Recommended Scheme": "பரிந்துரைக்கப்பட்ட திட்டம்",
        "Eligibility Status": "தகுதி நிலை",
        "Why Eligible?": "ஏன் தகுதியானது?",
        "Key Benefits": "முக்கிய நன்மைகள்",
        "Required Documents": "தேவையான ஆவணங்கள்",
        "Official Application Portal": "அதிகாரப்பூர்வ விண்ணப்ப தளம்",
        "Application Process": "விண்ணப்பிக்கும் முறை",
        "Match": "பொருத்தம்"
    }

    HINDI_MAP = {
        "Recommended Scheme": "अनुशंसित योजना",
        "Eligibility Status": "पात्रता की स्थिति",
        "Why Eligible?": "पात्रता का कारण",
        "Key Benefits": "मुख्य लाभ",
        "Required Documents": "आवश्यक दस्तावेज",
        "Official Application Portal": "आधिकारिक आवेदन पोर्टल",
        "Application Process": "आवेदन प्रक्रिया",
        "Match": "मैच"
    }

    @classmethod
    def translate(cls, text: str, target_lang: str) -> str:
        lang = target_lang.lower().strip()

        if lang in ["ta", "tamil"]:
            translated = text
            for en_term, ta_term in cls.TAMIL_MAP.items():
                translated = translated.replace(en_term, ta_term)
            return translated + "\n\n*(தமிழ் பதிப்பு)*"

        elif lang in ["hi", "hindi"]:
            translated = text
            for en_term, hi_term in cls.HINDI_MAP.items():
                translated = translated.replace(en_term, hi_term)
            return translated + "\n\n*(हिंदी संस्करण)*"

        return text

translation_agent = TranslationAgent()
