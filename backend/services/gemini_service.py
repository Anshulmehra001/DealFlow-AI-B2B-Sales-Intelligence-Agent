"""
Gemini AI service for agent intelligence
"""
import google.generativeai as genai
import logging
from typing import Dict, List, Optional
import json

from backend.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini API"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info("Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    async def generate_email(
        self,
        company_name: str,
        contact_name: str,
        email_type: str,
        context: Dict
    ) -> Dict[str, str]:
        """Generate personalized email using Gemini"""
        
        if not self.model:
            # Fallback to template if Gemini not available
            return self._generate_template_email(company_name, contact_name, email_type, context)
        
        try:
            prompt = self._build_email_prompt(company_name, contact_name, email_type, context)
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            text = response.text
            
            # Extract subject and body
            if "Subject:" in text and "Body:" in text:
                parts = text.split("Body:", 1)
                subject = parts[0].replace("Subject:", "").strip()
                body = parts[1].strip()
            else:
                subject = f"Quick question about {company_name}"
                body = text
            
            return {
                "subject": subject,
                "body_html": self._format_html_email(body)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate email with Gemini: {e}")
            return self._generate_template_email(company_name, contact_name, email_type, context)
    
    def _build_email_prompt(
        self,
        company_name: str,
        contact_name: str,
        email_type: str,
        context: Dict
    ) -> str:
        """Build prompt for email generation"""
        
        if email_type == "initial_outreach":
            return f"""
Write a professional B2B sales outreach email.

Company: {company_name}
Contact: {contact_name}
Industry: {context.get('industry', 'technology')}
Company Size: {context.get('company_size', 'mid-size')}

Requirements:
- Keep it under 150 words
- Personalize based on company details
- Mention 2-3 specific pain points for their industry
- Include a clear call-to-action
- Professional but friendly tone
- No pushy sales language

Format:
Subject: [subject line]
Body: [email body]
"""
        
        elif email_type == "follow_up":
            return f"""
Write a follow-up email for a B2B sales conversation.

Company: {company_name}
Contact: {contact_name}
Previous Context: {context.get('previous_context', 'We discussed improving sales efficiency')}

Requirements:
- Reference previous conversation
- Provide additional value
- Suggest specific meeting times
- Keep it brief (under 100 words)
- Professional tone

Format:
Subject: [subject line]
Body: [email body]
"""
        
        elif email_type == "proposal":
            deal_value = context.get('deal_value', 50000)
            return f"""
Write a proposal email for a B2B deal.

Company: {company_name}
Contact: {contact_name}
Deal Value: ${deal_value:,.0f}
Key Benefits: {', '.join(context.get('key_benefits', ['Increased efficiency', 'Cost savings']))}

Requirements:
- Professional and confident tone
- Highlight ROI and benefits
- Clear pricing
- Call-to-action for next steps
- Keep it under 200 words

Format:
Subject: [subject line]
Body: [email body]
"""
        
        return ""
    
    def _format_html_email(self, body: str) -> str:
        """Format plain text email as HTML"""
        # Convert line breaks to paragraphs
        paragraphs = body.split('\n\n')
        html_paragraphs = [f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip()]
        
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    {''.join(html_paragraphs)}
    <p>Best regards,<br>
    DealFlow AI Team</p>
</body>
</html>
"""
    
    def _generate_template_email(
        self,
        company_name: str,
        contact_name: str,
        email_type: str,
        context: Dict
    ) -> Dict[str, str]:
        """Fallback template-based email generation"""
        
        if email_type == "initial_outreach":
            subject = f"Quick question about {company_name}'s sales process"
            body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hi {contact_name},</p>
    
    <p>I noticed that {company_name} is growing, and I wanted to reach out.</p>
    
    <p>Many companies in your industry struggle with:</p>
    <ul>
        <li>Manual lead tracking and follow-ups</li>
        <li>Low conversion rates</li>
        <li>Inefficient sales processes</li>
    </ul>
    
    <p>We've helped similar companies increase their sales efficiency by 40% using AI-powered automation.</p>
    
    <p>Would you be open to a quick 15-minute call next week?</p>
    
    <p>Best regards,<br>
    DealFlow AI Team</p>
</body>
</html>
"""
        
        elif email_type == "follow_up":
            subject = f"Following up - {company_name}"
            body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hi {contact_name},</p>
    
    <p>I wanted to follow up on my previous email about helping {company_name} improve sales efficiency.</p>
    
    <p>I have a few time slots available this week:</p>
    <ul>
        <li>Tuesday at 2 PM</li>
        <li>Wednesday at 10 AM</li>
        <li>Thursday at 3 PM</li>
    </ul>
    
    <p>Would any of these work for a quick call?</p>
    
    <p>Best regards,<br>
    DealFlow AI Team</p>
</body>
</html>
"""
        
        else:  # proposal
            deal_value = context.get('deal_value', 50000)
            subject = f"Proposal for {company_name} - ${deal_value:,.0f}"
            body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <p>Hi {contact_name},</p>
    
    <p>Thank you for the great conversation! As discussed, here's our proposal for {company_name}.</p>
    
    <h3>Key Benefits:</h3>
    <ul>
        <li>40% increase in sales efficiency</li>
        <li>Automated lead nurturing</li>
        <li>AI-powered insights</li>
        <li>24/7 support</li>
    </ul>
    
    <h3>Investment:</h3>
    <p><strong>${deal_value:,.0f}</strong> annually</p>
    
    <p>Let's schedule a call to discuss next steps.</p>
    
    <p>Best regards,<br>
    DealFlow AI Team</p>
</body>
</html>
"""
        
        return {"subject": subject, "body_html": body}
    
    async def analyze_lead(self, lead_data: Dict) -> Dict:
        """Analyze lead and provide insights"""
        
        if not self.model:
            return {"insights": "Gemini not configured", "score_reasoning": "Default scoring applied"}
        
        try:
            prompt = f"""
Analyze this B2B lead and provide insights:

Company: {lead_data.get('company_name')}
Industry: {lead_data.get('industry')}
Company Size: {lead_data.get('company_size')}
Website: {lead_data.get('website')}
Tech Stack: {', '.join(lead_data.get('enriched_data', {}).get('tech_stack', []))}

Provide:
1. Key insights about this lead
2. Potential pain points they might have
3. Best approach for outreach
4. Estimated deal size range

Keep response under 150 words.
"""
            
            response = self.model.generate_content(prompt)
            
            return {
                "insights": response.text,
                "score_reasoning": "AI-powered analysis"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze lead: {e}")
            return {"insights": "Analysis unavailable", "score_reasoning": "Default scoring"}
    
    async def predict_deal_outcome(self, deal_data: Dict) -> Dict:
        """Predict deal outcome using Gemini"""
        
        if not self.model:
            return self._simple_prediction(deal_data)
        
        try:
            prompt = f"""
Analyze this B2B sales deal and predict the outcome:

Deal: {deal_data.get('deal_name')}
Value: ${deal_data.get('deal_value', 0):,.0f}
Stage: {deal_data.get('stage')}
Days in Stage: {deal_data.get('days_in_stage', 0)}
Activities: {len(deal_data.get('activities', []))}
Last Contact: {deal_data.get('days_since_contact', 'unknown')} days ago

Provide:
1. Close probability (0-100%)
2. Predicted close date (days from now)
3. Risk factors
4. Recommended actions

Format as JSON:
{{
  "probability": 75,
  "days_to_close": 30,
  "risk_factors": ["factor1", "factor2"],
  "recommendations": ["action1", "action2"]
}}
"""
            
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                result = json.loads(response.text)
                return result
            except:
                # Fallback to simple prediction
                return self._simple_prediction(deal_data)
            
        except Exception as e:
            logger.error(f"Failed to predict deal outcome: {e}")
            return self._simple_prediction(deal_data)
    
    def _simple_prediction(self, deal_data: Dict) -> Dict:
        """Simple rule-based prediction"""
        stage_probs = {
            "new": 10,
            "contacted": 20,
            "qualified": 40,
            "proposal": 60,
            "negotiation": 80,
            "closed_won": 100,
            "closed_lost": 0
        }
        
        probability = stage_probs.get(deal_data.get('stage', 'new'), 10)
        
        return {
            "probability": probability,
            "days_to_close": 30,
            "risk_factors": ["Limited data for prediction"],
            "recommendations": ["Increase engagement", "Schedule follow-up"]
        }


# Global Gemini service instance
gemini_service = GeminiService()
