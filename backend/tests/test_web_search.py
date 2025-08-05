"""
웹검색 매니저 테스트
"""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from backend.utils.web_search import WebSearchManager


class TestWebSearchManager:
    """웹검색 매니저 테스트 클래스"""
    
    @pytest.fixture
    def web_search_manager(self):
        """웹검색 매니저 인스턴스 생성"""
        return WebSearchManager()
    
    @pytest.fixture
    def mock_response(self):
        """모킹된 HTTP 응답"""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.content = b'<html><body><h1>Test Page</h1><p>Test content</p></body></html>'
        mock_resp.json.return_value = {
            'items': [
                {
                    'title': 'Test Minecraft Item',
                    'link': 'https://ftb.fandom.com/wiki/Test_Item',
                    'snippet': 'Test snippet content'
                }
            ]
        }
        return mock_resp
    
    @pytest.mark.unit
    def test_initialization(self, web_search_manager):
        """초기화 테스트"""
        assert web_search_manager is not None
        assert hasattr(web_search_manager, 'session')
        assert hasattr(web_search_manager, 'trusted_domains')
        assert hasattr(web_search_manager, 'blocked_domains')
        assert len(web_search_manager.trusted_domains) > 0
        assert len(web_search_manager.blocked_domains) > 0
    
    def test_trusted_domains_configuration(self, web_search_manager):
        """신뢰할 수 있는 도메인 설정 테스트"""
        trusted_domains = web_search_manager.trusted_domains
        
        assert 'ftb.fandom.com' in trusted_domains
        assert 'minecraft.fandom.com' in trusted_domains
        assert 'curseforge.com' in trusted_domains
        assert 'modrinth.com' in trusted_domains
    
    def test_blocked_domains_configuration(self, web_search_manager):
        """차단된 도메인 설정 테스트"""
        blocked_domains = web_search_manager.blocked_domains
        
        assert 'reddit.com' in blocked_domains
        assert 'youtube.com' in blocked_domains
        assert 'twitter.com' in blocked_domains
        assert 'facebook.com' in blocked_domains
    
    @pytest.mark.integration
    @patch.dict(os.environ, {
        'GOOGLE_CSE_API_KEY': 'test-api-key',
        'GOOGLE_CSE_ID': 'test-cse-id'
    })
    @patch('backend.utils.web_search.requests.Session.get')
    def test_google_search_success(self, mock_get, web_search_manager, mock_response):
        """Google 검색 성공 테스트"""
        mock_get.return_value = mock_response
        
        results = web_search_manager.search_minecraft_info('iron ore', 'TestModpack')
        
        assert len(results) > 0
        assert results[0]['title'] == 'Test Minecraft Item'
        assert results[0]['link'] == 'https://ftb.fandom.com/wiki/Test_Item'
        assert results[0]['source'] == 'google_search'
    
    @patch('backend.utils.web_search.requests.Session.get')
    def test_basic_web_search_success(self, mock_get, web_search_manager, mock_response):
        """기본 웹검색 성공 테스트"""
        mock_get.return_value = mock_response
        
        results = web_search_manager.search_minecraft_info('iron ore', 'TestModpack')
        
        # Google API 키가 없으면 기본 웹검색 사용
        assert isinstance(results, list)
    
    @patch('backend.utils.web_search.requests.Session.get')
    def test_google_search_api_error(self, mock_get, web_search_manager):
        """Google 검색 API 오류 테스트"""
        mock_get.side_effect = Exception("API Error")
        
        results = web_search_manager.search_minecraft_info('iron ore')
        
        assert results == []
    
    def test_is_trusted_domain_valid(self, web_search_manager):
        """유효한 신뢰할 수 있는 도메인 테스트"""
        valid_urls = [
            'https://ftb.fandom.com/wiki/Iron_Ore',
            'https://minecraft.fandom.com/wiki/Iron_Ore',
            'https://curseforge.com/minecraft/mc-mods/test-mod',
            'https://modrinth.com/mod/test-mod'
        ]
        
        for url in valid_urls:
            assert web_search_manager._is_trusted_domain(url) is True
    
    def test_is_trusted_domain_invalid(self, web_search_manager):
        """잘못된 도메인 테스트"""
        invalid_urls = [
            'https://reddit.com/r/minecraft',
            'https://youtube.com/watch?v=test',
            'https://twitter.com/minecraft',
            'https://facebook.com/minecraft',
            'https://malicious-site.com/fake',
            'invalid-url'
        ]
        
        for url in invalid_urls:
            assert web_search_manager._is_trusted_domain(url) is False
    
    def test_is_relevant_content_true(self, web_search_manager):
        """관련 콘텐츠 확인 성공 테스트"""
        query = "iron ore minecraft"
        relevant_titles = [
            "Iron Ore",
            "Minecraft Iron Ore Guide",
            "How to find Iron Ore in Minecraft",
            "Iron Ore Block"
        ]
        
        for title in relevant_titles:
            assert web_search_manager._is_relevant_content(title, query) is True
    
    def test_is_relevant_content_false(self, web_search_manager):
        """관련 콘텐츠 확인 실패 테스트"""
        query = "iron ore minecraft"
        irrelevant_titles = [
            "Diamond Ore",
            "Gold Block",
            "Wooden Pickaxe",
            "Completely Different Topic"
        ]
        
        for title in irrelevant_titles:
            assert web_search_manager._is_relevant_content(title, query) is False
    
    @patch('backend.utils.web_search.requests.Session.get')
    def test_extract_page_content_success(self, mock_get, web_search_manager, mock_response):
        """페이지 내용 추출 성공 테스트"""
        mock_get.return_value = mock_response
        
        content = web_search_manager.extract_page_content('https://ftb.fandom.com/wiki/Iron_Ore')
        
        assert 'title' in content
        assert 'url' in content
        assert 'content' in content
        assert 'crafting_info' in content
        assert content['url'] == 'https://ftb.fandom.com/wiki/Iron_Ore'
    
    @patch('backend.utils.web_search.requests.Session.get')
    def test_extract_page_content_error(self, mock_get, web_search_manager):
        """페이지 내용 추출 오류 테스트"""
        mock_get.side_effect = Exception("Network Error")
        
        content = web_search_manager.extract_page_content('https://invalid-url.com')
        
        assert 'error' in content
        assert content['url'] == 'https://invalid-url.com'
        assert content['title'] == ''
        assert content['content'] == ''
    
    def test_extract_snippet_success(self, web_search_manager):
        """스니펫 추출 성공 테스트"""
        from bs4 import BeautifulSoup
        
        html = '''
        <div>
            <a href="/wiki/Iron_Ore">Iron Ore</a>
            <p>Iron ore is a mineral block found underground.</p>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        link = soup.find('a')
        
        snippet = web_search_manager._extract_snippet(link)
        
        assert 'Iron ore is a mineral block' in snippet
    
    def test_extract_snippet_no_parent(self, web_search_manager):
        """부모 요소가 없는 스니펫 추출 테스트"""
        from bs4 import BeautifulSoup
        
        html = '<a href="/wiki/Iron_Ore">Iron Ore</a>'
        soup = BeautifulSoup(html, 'html.parser')
        link = soup.find('a')
        
        snippet = web_search_manager._extract_snippet(link)
        
        assert snippet == ""
    
    def test_search_query_construction(self, web_search_manager):
        """검색 쿼리 구성 테스트"""
        with patch.object(web_search_manager, '_google_search') as mock_google:
            mock_google.return_value = []
            
            # 모드팩 이름이 있는 경우
            web_search_manager.search_minecraft_info('iron ore', 'TestModpack')
            call_args = mock_google.call_args[0][0]
            
            assert 'TestModpack' in call_args
            assert 'minecraft modpack' in call_args
            assert 'iron ore' in call_args
            assert 'minecraft' in call_args
    
    def test_search_query_no_modpack(self, web_search_manager):
        """모드팩 이름이 없는 검색 쿼리 테스트"""
        with patch.object(web_search_manager, '_google_search') as mock_google:
            mock_google.return_value = []
            
            web_search_manager.search_minecraft_info('iron ore')
            call_args = mock_google.call_args[0][0]
            
            assert 'iron ore' in call_args
            assert 'minecraft' in call_args
            # 모드팩 관련 용어는 없어야 함
            assert 'modpack' not in call_args
    
    @patch('backend.utils.web_search.requests.Session.get')
    def test_parse_ftb_fandom_search(self, mock_get, web_search_manager, mock_response):
        """FTB Fandom 검색 결과 파싱 테스트"""
        from bs4 import BeautifulSoup
        
        html = '''
        <div class="searchresults">
            <a href="/wiki/Iron_Ore">Iron Ore</a>
            <a href="/wiki/Diamond_Ore">Diamond Ore</a>
            <a href="/external-link">External Link</a>
        </div>
        '''
        mock_response.content = html.encode()
        mock_get.return_value = mock_response
        
        soup = BeautifulSoup(html, 'html.parser')
        results = web_search_manager._parse_ftb_fandom_search(soup, 'iron ore')
        
        assert len(results) > 0
        assert any('Iron Ore' in result['title'] for result in results)
        assert all('ftb.fandom.com' in result['link'] for result in results)
        assert all(result['source'] == 'ftb_fandom' for result in results)
    
    @patch('backend.utils.web_search.requests.Session.get')
    def test_parse_minecraft_wiki_search(self, mock_get, web_search_manager, mock_response):
        """Minecraft Wiki 검색 결과 파싱 테스트"""
        from bs4 import BeautifulSoup
        
        html = '''
        <div class="searchresults">
            <a href="/wiki/Iron_Ore">Iron Ore</a>
            <a href="/wiki/Diamond_Ore">Diamond Ore</a>
        </div>
        '''
        mock_response.content = html.encode()
        mock_get.return_value = mock_response
        
        soup = BeautifulSoup(html, 'html.parser')
        results = web_search_manager._parse_minecraft_wiki_search(soup, 'iron ore')
        
        assert len(results) > 0
        assert all('minecraft.fandom.com' in result['link'] for result in results)
        assert all(result['source'] == 'minecraft_wiki' for result in results)
    
    def test_extract_quantity_success(self, web_search_manager):
        """수량 추출 성공 테스트"""
        from bs4 import BeautifulSoup
        
        test_cases = [
            ('<td>3</td>', 3),
            ('<td>Iron Ore x5</td>', 5),
            ('<td>Diamond x1</td>', 1),
            ('<td>Test Item</td>', 1),  # 숫자가 없으면 기본값 1
        ]
        
        for html, expected in test_cases:
            soup = BeautifulSoup(html, 'html.parser')
            cell = soup.find('td')
            quantity = web_search_manager._extract_quantity(cell)
            assert quantity == expected
    
    def test_parse_crafting_table_success(self, web_search_manager):
        """제작법 테이블 파싱 성공 테스트"""
        from bs4 import BeautifulSoup
        
        html = '''
        <table class="crafting">
            <tr>
                <td class="ingredient"><img alt="Iron Ore" src="iron.png"></td>
                <td class="ingredient"><img alt="Coal" src="coal.png"></td>
                <td class="result"><img alt="Iron Ingot" src="iron_ingot.png">x1</td>
            </tr>
        </table>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        
        recipe_data = web_search_manager._parse_crafting_table(table)
        
        assert 'result_item' in recipe_data
        assert 'ingredients' in recipe_data
        assert recipe_data['result_item'] == 'Iron Ingot'
        assert len(recipe_data['ingredients']) == 2
        assert recipe_data['ingredients'][0]['item'] == 'Iron Ore'
        assert recipe_data['ingredients'][1]['item'] == 'Coal'
    
    def test_parse_crafting_table_empty(self, web_search_manager):
        """빈 제작법 테이블 파싱 테스트"""
        from bs4 import BeautifulSoup
        
        html = '<table class="crafting"><tr><td>No recipe data</td></tr></table>'
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        
        recipe_data = web_search_manager._parse_crafting_table(table)
        
        assert recipe_data == {}
    
    @patch('backend.utils.web_search.requests.Session.get')
    def test_extract_crafting_info_success(self, mock_get, web_search_manager, mock_response):
        """제작법 정보 추출 성공 테스트"""
        from bs4 import BeautifulSoup
        
        html = '''
        <div id="mw-content-text">
            <table class="crafting">
                <tr>
                    <td class="ingredient"><img alt="Iron Ore"></td>
                    <td class="result"><img alt="Iron Ingot"></td>
                </tr>
            </table>
        </div>
        '''
        mock_response.content = html.encode()
        mock_get.return_value = mock_response
        
        content = web_search_manager.extract_page_content('https://ftb.fandom.com/wiki/Iron_Ingot')
        
        assert 'crafting_info' in content
        assert isinstance(content['crafting_info'], dict)
    
    def test_search_minecraft_info_exception_handling(self, web_search_manager):
        """검색 중 예외 처리 테스트"""
        with patch.object(web_search_manager, '_google_search', side_effect=Exception("Test error")):
            results = web_search_manager.search_minecraft_info('iron ore')
            
            assert results == []
    
    def test_extract_page_content_timeout(self, web_search_manager):
        """페이지 내용 추출 타임아웃 테스트"""
        with patch('backend.utils.web_search.requests.Session.get', side_effect=Exception("Timeout")):
            content = web_search_manager.extract_page_content('https://slow-site.com')
            
            assert 'error' in content
            assert 'Timeout' in content['error']
    
    def test_user_agent_header(self, web_search_manager):
        """User-Agent 헤더 설정 테스트"""
        headers = web_search_manager.session.headers
        
        assert 'User-Agent' in headers
        assert 'Chrome' in headers['User-Agent']
        assert 'Windows' in headers['User-Agent']
    
    def test_search_sites_configuration(self, web_search_manager):
        """검색 사이트 구성 테스트"""
        with patch.object(web_search_manager, '_search_site') as mock_search:
            mock_search.return_value = []
            
            web_search_manager._basic_web_search('iron ore')
            
            # 주요 사이트들이 호출되었는지 확인
            call_args = [call[0][0] for call in mock_search.call_args_list]
            
            assert any('ftb.fandom.com' in url for url in call_args)
            assert any('ftbwiki.org' in url for url in call_args)
            assert any('minecraft.fandom.com' in url for url in call_args)
    
    def test_result_limit_enforcement(self, web_search_manager):
        """결과 제한 적용 테스트"""
        # 많은 결과를 반환하는 모킹
        many_results = [{'title': f'Result {i}', 'link': f'link{i}', 'snippet': 'test'} for i in range(10)]
        
        with patch.object(web_search_manager, '_google_search', return_value=many_results):
            results = web_search_manager.search_minecraft_info('iron ore')
            
            # Google 검색은 최대 5개 결과
            assert len(results) <= 5
    
    def test_basic_web_search_result_limit(self, web_search_manager):
        """기본 웹검색 결과 제한 테스트"""
        many_results = [{'title': f'Result {i}', 'link': f'link{i}', 'snippet': 'test'} for i in range(10)]
        
        with patch.object(web_search_manager, '_search_site', return_value=many_results):
            results = web_search_manager._basic_web_search('iron ore')
            
            # 기본 웹검색도 최대 5개 결과
            assert len(results) <= 5 