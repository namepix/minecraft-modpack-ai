import os
import json
import logging
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class WebSearchManager:
    def __init__(self):
        """웹검색 매니저를 초기화합니다."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 신뢰할 수 있는 도메인 목록
        self.trusted_domains = [
            'ftb.fandom.com',
            'ftbwiki.org',
            'wiki.gg',
            'curseforge.com',
            'modrinth.com',
            'minecraft.fandom.com',
            'minecraft.wiki'
        ]
        
        # 차단할 도메인 목록
        self.blocked_domains = [
            'reddit.com',
            'youtube.com',
            'twitter.com',
            'facebook.com'
        ]
    
    def search_minecraft_info(self, query: str, modpack_name: str = None) -> List[Dict]:
        """마인크래프트 관련 정보를 검색합니다."""
        try:
            # 검색 쿼리 구성
            search_terms = []
            if modpack_name:
                search_terms.append(f'"{modpack_name}" minecraft modpack')
            search_terms.append(query)
            search_terms.append('minecraft')
            
            search_query = ' '.join(search_terms)
            
            # Google Custom Search API 사용 (선택사항)
            if os.getenv('GOOGLE_CSE_API_KEY') and os.getenv('GOOGLE_CSE_ID'):
                return self._google_search(search_query)
            else:
                # 기본 웹 크롤링 검색
                return self._basic_web_search(search_query)
                
        except Exception as e:
            logger.error(f"웹검색 실패: {e}")
            return []
    
    def _google_search(self, query: str) -> List[Dict]:
        """Google Custom Search API를 사용한 검색."""
        try:
            api_key = os.getenv('GOOGLE_CSE_API_KEY')
            cse_id = os.getenv('GOOGLE_CSE_ID')
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': cse_id,
                'q': query,
                'num': 5,  # 최대 5개 결과
                'safe': 'active'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                if self._is_trusted_domain(item.get('link', '')):
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'google_search'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Google 검색 실패: {e}")
            return []
    
    def _basic_web_search(self, query: str) -> List[Dict]:
        """기본 웹 크롤링을 통한 검색."""
        try:
            # 주요 마인크래프트 위키 사이트들을 직접 검색
            search_sites = [
                f'https://ftb.fandom.com/wiki/Special:Search?query={query}',
                f'https://ftbwiki.org/index.php?search={query}',
                f'https://minecraft.fandom.com/wiki/Special:Search?query={query}'
            ]
            
            results = []
            
            for site_url in search_sites:
                try:
                    site_results = self._search_site(site_url, query)
                    results.extend(site_results)
                    time.sleep(1)  # 요청 간격 조절
                except Exception as e:
                    logger.warning(f"사이트 검색 실패 {site_url}: {e}")
                    continue
            
            return results[:5]  # 최대 5개 결과
            
        except Exception as e:
            logger.error(f"기본 웹검색 실패: {e}")
            return []
    
    def _search_site(self, search_url: str, query: str) -> List[Dict]:
        """특정 사이트에서 검색을 수행합니다."""
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # 사이트별 검색 결과 파싱
            if 'ftb.fandom.com' in search_url:
                results = self._parse_ftb_fandom_search(soup, query)
            elif 'ftbwiki.org' in search_url:
                results = self._parse_ftbwiki_search(soup, query)
            elif 'minecraft.fandom.com' in search_url:
                results = self._parse_minecraft_wiki_search(soup, query)
            
            return results
            
        except Exception as e:
            logger.error(f"사이트 검색 실패 {search_url}: {e}")
            return []
    
    def _parse_ftb_fandom_search(self, soup: BeautifulSoup, query: str) -> List[Dict]:
        """FTB Fandom 검색 결과를 파싱합니다."""
        results = []
        
        # 검색 결과 링크 찾기
        search_results = soup.find_all('a', href=True)
        
        for link in search_results:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # 위키 페이지 링크인지 확인
            if '/wiki/' in href and not href.startswith('http'):
                full_url = urljoin('https://ftb.fandom.com', href)
                
                if self._is_relevant_content(title, query):
                    results.append({
                        'title': title,
                        'link': full_url,
                        'snippet': self._extract_snippet(link),
                        'source': 'ftb_fandom'
                    })
        
        return results[:3]  # 상위 3개 결과
    
    def _parse_ftbwiki_search(self, soup: BeautifulSoup, query: str) -> List[Dict]:
        """FTB Wiki 검색 결과를 파싱합니다."""
        results = []
        
        # 검색 결과 링크 찾기
        search_results = soup.find_all('a', href=True)
        
        for link in search_results:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # 위키 페이지 링크인지 확인
            if 'index.php?title=' in href and not href.startswith('http'):
                full_url = urljoin('https://ftbwiki.org', href)
                
                if self._is_relevant_content(title, query):
                    results.append({
                        'title': title,
                        'link': full_url,
                        'snippet': self._extract_snippet(link),
                        'source': 'ftbwiki'
                    })
        
        return results[:3]  # 상위 3개 결과
    
    def _parse_minecraft_wiki_search(self, soup: BeautifulSoup, query: str) -> List[Dict]:
        """Minecraft Wiki 검색 결과를 파싱합니다."""
        results = []
        
        # 검색 결과 링크 찾기
        search_results = soup.find_all('a', href=True)
        
        for link in search_results:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # 위키 페이지 링크인지 확인
            if '/wiki/' in href and not href.startswith('http'):
                full_url = urljoin('https://minecraft.fandom.com', href)
                
                if self._is_relevant_content(title, query):
                    results.append({
                        'title': title,
                        'link': full_url,
                        'snippet': self._extract_snippet(link),
                        'source': 'minecraft_wiki'
                    })
        
        return results[:3]  # 상위 3개 결과
    
    def _is_relevant_content(self, title: str, query: str) -> bool:
        """제목이 쿼리와 관련이 있는지 확인합니다."""
        query_terms = query.lower().split()
        title_lower = title.lower()
        
        # 쿼리 용어 중 하나라도 제목에 포함되어 있는지 확인
        return any(term in title_lower for term in query_terms if len(term) > 2)
    
    def _extract_snippet(self, element) -> str:
        """요소에서 스니펫을 추출합니다."""
        # 부모 요소에서 텍스트 추출
        parent = element.parent
        if parent:
            text = parent.get_text(strip=True)
            # 제목을 제외한 텍스트 반환
            title = element.get_text(strip=True)
            if title in text:
                snippet = text.replace(title, '').strip()
                return snippet[:200] + '...' if len(snippet) > 200 else snippet
        
        return ""
    
    def _is_trusted_domain(self, url: str) -> bool:
        """URL이 신뢰할 수 있는 도메인인지 확인합니다."""
        try:
            domain = urlparse(url).netloc.lower()
            
            # 차단된 도메인 확인
            for blocked in self.blocked_domains:
                if blocked in domain:
                    return False
            
            # 신뢰할 수 있는 도메인 확인
            for trusted in self.trusted_domains:
                if trusted in domain:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def extract_page_content(self, url: str) -> Dict:
        """웹페이지에서 내용을 추출합니다."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 제목 추출
            title = ""
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # 본문 내용 추출
            content = ""
            
            # 위키 페이지의 경우 메인 콘텐츠 영역 찾기
            main_content = soup.find('div', {'id': 'mw-content-text'}) or \
                          soup.find('div', {'class': 'mw-parser-output'}) or \
                          soup.find('div', {'class': 'content'})
            
            if main_content:
                # 불필요한 요소 제거
                for elem in main_content.find_all(['script', 'style', 'nav', 'footer']):
                    elem.decompose()
                
                content = main_content.get_text(strip=True)
            else:
                # 일반적인 본문 추출
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # 제작법 정보 추출 (특별 처리)
            crafting_info = self._extract_crafting_info(soup)
            
            return {
                'title': title,
                'url': url,
                'content': content[:2000],  # 내용 길이 제한
                'crafting_info': crafting_info,
                'extracted_at': str(time.time())
            }
            
        except Exception as e:
            logger.error(f"페이지 내용 추출 실패 {url}: {e}")
            return {
                'title': '',
                'url': url,
                'content': '',
                'crafting_info': {},
                'error': str(e)
            }
    
    def _extract_crafting_info(self, soup: BeautifulSoup) -> Dict:
        """페이지에서 제작법 정보를 추출합니다."""
        crafting_info = {}
        
        try:
            # 제작법 테이블 찾기
            crafting_tables = soup.find_all('table', {'class': re.compile(r'crafting|recipe', re.I)})
            
            for table in crafting_tables:
                # 제작법 정보 파싱
                recipe_data = self._parse_crafting_table(table)
                if recipe_data:
                    crafting_info.update(recipe_data)
            
            return crafting_info
            
        except Exception as e:
            logger.error(f"제작법 정보 추출 실패: {e}")
            return {}
    
    def _parse_crafting_table(self, table) -> Dict:
        """제작법 테이블을 파싱합니다."""
        try:
            recipe_data = {}
            
            # 결과 아이템 찾기
            result_cell = table.find('td', {'class': re.compile(r'result|output', re.I)})
            if result_cell:
                result_img = result_cell.find('img')
                if result_img:
                    recipe_data['result_item'] = result_img.get('alt', '')
                    recipe_data['result_quantity'] = self._extract_quantity(result_cell)
            
            # 재료 아이템들 찾기
            ingredients = []
            ingredient_cells = table.find_all('td', {'class': re.compile(r'ingredient|input', re.I)})
            
            for cell in ingredient_cells:
                img = cell.find('img')
                if img:
                    ingredient = {
                        'item': img.get('alt', ''),
                        'quantity': self._extract_quantity(cell)
                    }
                    ingredients.append(ingredient)
            
            recipe_data['ingredients'] = ingredients
            
            return recipe_data
            
        except Exception as e:
            logger.error(f"제작법 테이블 파싱 실패: {e}")
            return {}
    
    def _extract_quantity(self, cell) -> int:
        """셀에서 수량을 추출합니다."""
        try:
            text = cell.get_text(strip=True)
            # 숫자 패턴 찾기
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
            return 1
        except:
            return 1 