from typing import Optional, Dict, List
import aiohttp
from bs4 import BeautifulSoup



class SRORegistryService:
    """Сервис для работы с реестрами СРО."""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получает HTTP сессию."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def check_membership_status(self, organization_name: str) -> Optional[Dict]:
        """Проверяет статус членства организации в реестре СРО."""
        print(f"[SRORegistryService] Checking membership for: {organization_name}")
        try:
            # Пытаемся найти в разных реестрах
            registries = [
                self._check_noso_registry,  # Проверяем сначала СРО НОСО
                self._check_nostroy_registry,
                self._check_nopriz_registry,
                self._check_federal_registry
            ]
            
            for check_func in registries:
                try:
                    print(f"[SRORegistryService] Trying registry: {check_func.__name__}")
                    result = await check_func(organization_name)
                    if result:
                        print(f"[SRORegistryService] Found in registry: {result.get('registry')}")
                        return result
                except Exception as e:
                    print(f"[SRORegistryService] Error checking {check_func.__name__}: {str(e)}")
                    continue
            
            print("[SRORegistryService] Organization not found in any registry")
            return None
            
        except Exception as e:
            print(f"[SRORegistryService] Critical error: {str(e)}")
            return None
    
    async def _check_nostroy_registry(self, organization_name: str) -> Optional[Dict]:
        """Проверяет в реестре НОСТРОЙ."""
        try:
            session = await self._get_session()
            
            # Пример URL для API НОСТРОЙ (реальный может отличаться)
            url = "https://reestr.nostroy.ru/api/search"
            params = {
                "name": organization_name,
                "type": "organization"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("organizations"):
                        org = data["organizations"][0]
                        return {
                            "registry": "НОСТРОЙ",
                            "name": org.get("name"),
                            "inn": org.get("inn"),
                            "status": org.get("status"),
                            "join_date": org.get("join_date"),
                            "sro_name": org.get("sro_name"),
                            "registry_url": "https://reestr.nostroy.ru"
                        }
            
            return None
            
        except Exception:
            return None
    
    async def _check_nopriz_registry(self, organization_name: str) -> Optional[Dict]:
        """Проверяет в реестре НОПРИЗ."""
        try:
            session = await self._get_session()
            
            # Пример URL для API НОПРИЗ (реальный может отличаться)
            url = "https://reestr.nopriz.ru/api/organizations"
            params = {
                "search": organization_name
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("items"):
                        org = data["items"][0]
                        return {
                            "registry": "НОПРИЗ",
                            "name": org.get("name"),
                            "inn": org.get("inn"),
                            "status": org.get("status"),
                            "join_date": org.get("join_date"),
                            "sro_name": org.get("sro_name"),
                            "registry_url": "https://reestr.nopriz.ru"
                        }
            
            return None
            
        except Exception:
            return None
    
    async def _check_federal_registry(self, organization_name: str) -> Optional[Dict]:
        """Проверяет в федеральном реестре."""
        try:
            session = await self._get_session()
            
            # Пример URL для федерального реестра
            url = "https://reestr.gosstroy.gov.ru/api/organizations"
            params = {
                "q": organization_name
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("results"):
                        org = data["results"][0]
                        return {
                            "registry": "Федеральный реестр",
                            "name": org.get("name"),
                            "inn": org.get("inn"),
                            "status": org.get("status"),
                            "join_date": org.get("join_date"),
                            "sro_name": org.get("sro_name"),
                            "registry_url": "https://reestr.gosstroy.gov.ru"
                        }
            
            return None
            
        except Exception:
            return None

    async def _check_noso_registry(self, organization_name: str, inn: str = "") -> Optional[Dict]:
        """Проверяет в реестре СРО НОСО."""
        print(f"[_check_noso_registry] Checking {organization_name} (INN: {inn})")
        try:
            session = await self._get_session()
            base_url = "https://www.sronoso.ru/reestr/"
            
            params = {
                "PAGEN_1": 1,
                "arrFilter_ff[NAME]": organization_name,
                "arrFilter_pf[STATUS]": "",
                "arrFilter_pf[INNNumber]": inn,
                "set_filter": "Y"
            }
            
            async with session.get(base_url, params=params) as response:
                if response.status != 200:
                    print(f"[_check_noso_registry] HTTP error: {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                table = soup.find('table', {'class': 'table table-bordered table-striped'})
                
                if not table:
                    print("[_check_noso_registry] No results table found")
                    return None
                    
                rows = table.find_all('tr')
                if len(rows) <= 1:  # Только заголовки
                    print("[_check_noso_registry] No results in table")
                    return None
                    
                # Ищем точное совпадение по названию организации
                for row in rows[1:]:  # Пропускаем заголовок
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        org_name = cols[1].text.strip()
                        status = cols[0].text.strip()
                        org_inn = cols[2].text.strip()
                        join_date = cols[3].text.strip()
                        
                        print(f"[_check_noso_registry] Found: {org_name} ({org_inn})")
                        
                        if organization_name.lower() == org_name.lower():
                            return {
                                "registry": "СРО НОСО",
                                "name": org_name,
                                "inn": org_inn,
                                "status": status,
                                "join_date": join_date,
                                "sro_name": "СРО НОСО",
                                "registry_url": response.url.human_repr()
                            }
            
            print("[_check_noso_registry] No exact match found")
            return None
            
        except Exception:
            return None
    
    async def get_organization_by_inn(self, inn: str) -> Optional[Dict]:
        """Получает информацию об организации по ИНН."""
        try:
            session = await self._get_session()
            
            # Пример запроса к API ФНС или другому сервису
            url = "https://api.tax.gov.ru/organizations"
            params = {"inn": inn}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("organization")
            
            return None
            
        except Exception:
            return None
    
    async def get_sro_members_list(self, sro_name: str) -> List[Dict]:
        """Получает список членов конкретной СРО."""
        try:
            session = await self._get_session()
            
            # Пример запроса к API реестра
            url = f"https://reestr.nostroy.ru/api/sro/{sro_name}/members"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("members", [])
            
            return []
            
        except Exception:
            return []
    
    async def verify_specialist_certificate(self, specialist_id: str) -> Optional[Dict]:
        """Проверяет сертификат специалиста в НРС."""
        try:
            session = await self._get_session()
            
            # Пример запроса к Национальному реестру специалистов
            url = f"https://nrs.nostroy.ru/api/specialists/{specialist_id}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "specialist_id": data.get("id"),
                        "name": data.get("name"),
                        "qualification": data.get("qualification"),
                        "certificate_number": data.get("certificate_number"),
                        "valid_until": data.get("valid_until"),
                        "status": data.get("status")
                    }
            
            return None
            
        except Exception:
            return None
    
    async def close(self) -> None:
        """Закрывает HTTP сессию."""
        if self.session and not self.session.closed:
            await self.session.close()
