from typing import Dict, Any, List

class ExplanationAgent:
    """
    Independent Explanation Agent module:
    Generates structured markdown explanations containing:
    - Why recommended
    - Benefits
    - Eligibility explanation
    - Application process
    - Required documents
    - Official portal link
    """
    @staticmethod
    def format_explanation(grounded_text: str, verified_items: List[Dict[str, Any]]) -> str:
        eligible_items = [it for it in verified_items if it["rule_evaluation"]["is_eligible"]]

        if not eligible_items:
            return grounded_text

        top = eligible_items[0]
        scheme = top["scheme"]
        
        # Append application process & official portal validation
        app_process = (
            f"\n\n### 📝 Application Process:\n"
            f"1. Visit the official government portal: [{scheme.get('application_url') or scheme.get('official_application_url')}]({scheme.get('application_url') or scheme.get('official_application_url')}).\n"
            f"2. Fill in the online registration form with verified demographic details.\n"
            f"3. Upload mandatory documents ({', '.join(scheme.get('documents_required') or scheme.get('required_documents') or [])}).\n"
            f"4. Submit for administrative verification and tracking."
        )

        return grounded_text + app_process

explanation_agent = ExplanationAgent()
