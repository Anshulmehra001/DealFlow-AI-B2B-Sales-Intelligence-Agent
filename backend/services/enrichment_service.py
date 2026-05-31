"""
Lead enrichment service using web scraping
"""
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
import re
from urllib.parse import urlparse

from backend.config import settings

logger = logging.getLogger(__name__)


class EnrichmentService:
    """Service for enriching lead data from public sources"""
    
    def __init__(self):
        self.timeout = 10.0
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    async def enrich_lead(self, company_name: str, website: Optional[str] = None) -> Dict:
        """Enrich lead with public data"""
        enriched_data = {
            "tech_stack": [],
            "keywords": [],
            "social_media": {},
            "recent_news": [],
            "employee_count_estimate": None,
            "funding_stage": None
        }
        
        if not settings.ENABLE_WEB_SCRAPING or not website:
            return enriched_data
        
        try:
            # Scrape company website
            website_data = await self._scrape_website(website)
            enriched_data.update(website_data)
            
            # Extract tech stack from website
            tech_stack = await self._detect_tech_stack(website)
            enriched_data["tech_stack"] = tech_stack
            
            logger.info(f"Successfully enriched lead: {company_name}")
            
        except Exception as e:
            logger.error(f"Failed to enrich lead {company_name}: {e}")
        
        return enriched_data
    
    async def _scrape_website(self, url: str) -> Dict:
        """Scrape company website for information"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract metadata
                data = {
                    "keywords": self._extract_keywords(soup),
                    "social_media": self._extract_social_links(soup),
                }
                
                return data
                
        except Exception as e:
            logger.error(f"Failed to scrape website {url}: {e}")
            return {}
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from website"""
        keywords = []
        
        # From meta tags
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords and meta_keywords.get("content"):
            keywords.extend([k.strip() for k in meta_keywords["content"].split(",")])
        
        # From meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            # Extract important words (simple approach)
            desc_words = re.findall(r'\b[A-Z][a-z]+\b', meta_desc["content"])
            keywords.extend(desc_words[:5])
        
        # From headings
        for heading in soup.find_all(['h1', 'h2']):
            text = heading.get_text().strip()
            if text and len(text) < 50:
                keywords.append(text)
        
        # Remove duplicates and limit
        return list(set(keywords))[:10]
    
    def _extract_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links"""
        social_media = {}
        
        social_patterns = {
            "linkedin": r"linkedin\.com/company/",
            "twitter": r"twitter\.com/",
            "facebook": r"facebook\.com/",
            "github": r"github\.com/",
            "youtube": r"youtube\.com/"
        }
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href):
                    social_media[platform] = href
                    break
        
        return social_media
    
    async def _detect_tech_stack(self, url: str) -> List[str]:
        """Detect technology stack from website"""
        tech_stack = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(url, headers=headers, follow_redirects=True)
                
                html = response.text
                headers_dict = dict(response.headers)
                
                # Detect from HTML content
                tech_indicators = {
                    "React": ["react", "_react", "reactjs"],
                    "Vue.js": ["vue.js", "vuejs", "__vue__"],
                    "Angular": ["ng-", "angular"],
                    "WordPress": ["wp-content", "wordpress"],
                    "Shopify": ["shopify", "cdn.shopify"],
                    "Next.js": ["_next", "next.js"],
                    "Node.js": ["node", "nodejs"],
                    "Django": ["django", "csrftoken"],
                    "Rails": ["rails", "ruby"],
                    "MongoDB": ["mongodb"],
                    "PostgreSQL": ["postgresql", "postgres"],
                }
                
                html_lower = html.lower()
                for tech, indicators in tech_indicators.items():
                    if any(indicator in html_lower for indicator in indicators):
                        tech_stack.append(tech)
                
                # Detect from headers
                server = headers_dict.get("server", "").lower()
                if "nginx" in server:
                    tech_stack.append("Nginx")
                elif "apache" in server:
                    tech_stack.append("Apache")
                
                # Detect from powered-by header
                powered_by = headers_dict.get("x-powered-by", "").lower()
                if "express" in powered_by:
                    tech_stack.append("Express.js")
                elif "php" in powered_by:
                    tech_stack.append("PHP")
                
        except Exception as e:
            logger.error(f"Failed to detect tech stack for {url}: {e}")
        
        return list(set(tech_stack))
    
    def estimate_company_size(self, website_data: Dict) -> Optional[str]:
        """Estimate company size from available data"""
        # This is a simplified estimation
        # In production, you'd use LinkedIn API or similar
        
        keywords = website_data.get("keywords", [])
        
        size_indicators = {
            "enterprise": ["1000+", "Enterprise", "Fortune 500"],
            "large": ["201-1000", "Large", "Established"],
            "medium": ["51-200", "Growing", "Scale-up"],
            "small": ["11-50", "Startup", "Small"],
            "startup": ["1-10", "Seed", "Early-stage"]
        }
        
        for size, indicators in size_indicators.items():
            if any(indicator.lower() in " ".join(keywords).lower() for indicator in indicators):
                return size
        
        return None
    
    async def search_company_news(self, company_name: str) -> List[str]:
        """Search for recent company news (simplified)"""
        # In production, you'd use News API or similar
        # For now, return empty list
        return []
    
    def extract_domain_from_email(self, email: str) -> Optional[str]:
        """Extract domain from email address"""
        try:
            domain = email.split("@")[1]
            return f"https://{domain}"
        except:
            return None


# Global enrichment service instance
enrichment_service = EnrichmentService()
