# БЛОК 1: ИМПОРТ НЕОБХОДИМЫХ БИБЛИОТЕК
import matplotlib
matplotlib.use('Agg') # Отключение GUI-рендеринга для matplotlib
from sympy import symbols # Символьная математика для расчета порога
import matplotlib.pyplot as plt 
import base64 # Кодирование графиков в строку для передачи в HTML
from io import BytesIO
from datetime import datetime
import re # Регулярные выражения — для поиска WSDL-паттернов в запросах

# БЛОК 2: МОДУЛЬ ЗАЩИТЫ ОТ WSDL-СКАНИРОВАНИЯ (УБИ.151)
WSDL_INDICATORS = [
    r'[Ww][Ss][Dd][Ll]',
    r'\?wsdl',
    r'/[Ss]ervices\?',
    r'/[Ss]ervice\.',
    r'SOAPAction',
    r'<wsdl:',
    r'GetServices',
    r'GetPortType',
    r'GetBinding',
    r'\.wsdl',
] # Список паттернов, характерных для WSDL-запросов

def is_wsdl_request(url='', headers=None, body=''):   # Проверяет URL, заголовки и первые 500 байт тела запроса
    # Возвращает True, если запрос похож на WSDL-сканирование
    if headers is None:
        headers = {}
    if 'wsdl' in url.lower() or '?wsdl' in url.lower() or '/service' in url.lower():
        return True
    headers_str = str(headers).lower()
    if 'soapaction' in headers_str or 'wsdl' in headers_str:
        return True
    body_check = body[:500] if body else ''
    for pattern in WSDL_INDICATORS:
        if re.search(pattern, body_check, re.IGNORECASE):
            return True
    return False

def generate_fake_wsdl(ip_address, attempt_number=1): # При attempt_number > 3 — возвращает "AccessDenied"
    # При первых попытках — возвращает правдоподобный фейковый XML с несуществующим адресом сервиса https://api.telecom.service/fake
    if attempt_number > 3:
        return '''<?xml version="1.0"?>
<wsdl:definitions name="AccessDenied" 
    xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/">
    <wsdl:message name="AccessDenied">
        <wsdl:part name="error" type="xsd:string"/>
    </wsdl:message>
</wsdl:definitions>'''

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions name="TelecomService" 
    targetNamespace="http://tempuri.org/"
    xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/">
    <wsdl:types>
        <xsd:schema targetNamespace="http://tempuri.org/"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <xsd:element name="DummyRequest">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="Data" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </wsdl:types>
    <wsdl:service name="TelecomService">
        <wsdl:port name="TelecomPort" binding="tns:TelecomBinding">
            <soap:address location="https://api.telecom.service/fake"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>'''

class WSDLProtector:
    def __init__(self, rate_limit=180):
        self.rate_limit = rate_limit
        self.attackers_log = {} # {ip: количество WSDL-попыток}
        self.fake_responses = {} # {ip: сколько фейков отправлено}
        self.wsdl_attacks = [] # полный лог всех атак с временными метками

    # Фиксируем атаку, увеличиваем счётчик попыток
    # Генерируем фейковый WSDL и возвращаем статус 'FAKE_WSDL'
    def check_request(self, ip_address, request_count, url='', headers=None, body=''):
        if headers is None:
            headers = {}

        # Проверка на WSDL-сканирование
        if is_wsdl_request(url, headers, body):
            self.attackers_log[ip_address] = self.attackers_log.get(ip_address, 0) + 1
            attempt = self.attackers_log[ip_address]

            self.wsdl_attacks.append({
                'ip': ip_address,
                'timestamp': datetime.now(),
                'attempt': attempt,
                'url': url[:100]
            })

            fake_wsdl = generate_fake_wsdl(ip_address, attempt)
            self.fake_responses[ip_address] = self.fake_responses.get(ip_address, 0) + 1
            return 'FAKE_WSDL', fake_wsdl, 'wsdl_scan'

        # Проверка rate limiting
        if request_count > self.rate_limit:
            return 'BLOCK_RATE', f'Rate limit exceeded: {request_count} > {self.rate_limit}', 'rate_limit'

        return 'ALLOW', None, 'normal'

    def get_stats(self):
        return {
            'total_wsdl_attacks': len(self.wsdl_attacks),
            'total_fake_responses': sum(self.fake_responses.values()),
            'unique_attackers': len(self.attackers_log),
            'attacks_detail': self.wsdl_attacks[-10:]
        }

# БЛОК 3: РАСЧЕТ ПОРОГА БЛОКИРОВКИ

R, T, N = symbols("R T N") # R — базовый RPS, T — окно в сек, N — число IP
BASE_RPS = 120 # Разрешённый трафик всего: 120 запросов/сек
WINDOW = 60 # Временное окно: 60 секунд
IPS_COUNT = 40 # Количество IP в сети

threshold_expr = (R * T) / N # Формула: суммарный трафик / число IP
THRESHOLD = float(threshold_expr.subs({R: BASE_RPS, T: WINDOW, N: IPS_COUNT}))
print(f"Порог блокировки: {THRESHOLD:.0f} запросов за {WINDOW} сек")

# БЛОК 4: ВХОДНЫЕ ДАННЫЕ (IP-АДРЕСА И ЗАПРОСЫ)

ip_addresses = [
    "192.165.1.10", "192.168.1.11", "10.0.0.5", "192.168.1.12",
    "172.16.0.3", "192.165.1.13", "10.0.0.15", "192.168.1.14",
    "192.168.1.15", "10.0.0.20"
]

requests_per_ip = [183, 60, 190, 60, 187, 49, 203, 39, 60, 198]

# БЛОК 5: ДОБАВЛЕНИЕ WSDL-АТАК ДЛЯ ДЕМОНСТРАЦИИ

# СПИСОК IP, КОТОРЫЕ БУДУТ СЧИТАТЬСЯ WSDL-СКАНЕРАМИ (для демонстрации)
# В реальном приложении эти данные определяются автоматически
WSDL_ATTACKER_IPS = ["192.165.1.10", "10.0.0.5", "172.16.0.3", "10.0.0.15"]

# КОЛИЧЕСТВО ПОПЫТОК WSDL ДЛЯ КАЖДОГО АТАКУЮЩЕГО
WSDL_ATTEMPTS_MAP = {
    "192.165.1.10": 3,
    "10.0.0.5": 2,
    "172.16.0.3": 5,
    "10.0.0.15": 1,
}

# БЛОК 6: ОБРАБОТКА ЗАПРОСОВ И ПРИМЕНЕНИЕ ЗАЩИТЫ
protector = WSDLProtector(rate_limit=THRESHOLD)

blocked_status = []
blocked_ips = []
allowed_ips = []
wsdl_attack_ips = []
fake_wsdl_sent_ips = []

print("\n" + "="*60)
print("ОБРАБОТКА ЗАПРОСОВ С WSDL-ЗАЩИТОЙ")
print("="*60)

# Сначала вручную заполняем лог для WSDL-атакующих (демо-данные)
for ip in WSDL_ATTACKER_IPS:
    attempts = WSDL_ATTEMPTS_MAP.get(ip, 1)
    protector.attackers_log[ip] = attempts
    protector.fake_responses[ip] = attempts
    for a in range(attempts):
        protector.wsdl_attacks.append({
            'ip': ip,
            'timestamp': datetime.now(),
            'attempt': a + 1,
            'url': '/service.asmx?wsdl'
        })
    wsdl_attack_ips.append(ip)
    fake_wsdl_sent_ips.append(ip)

# Обработка каждого IP
for i, ip in enumerate(ip_addresses):
    url = "/api/send_sms"

    # Если IP в списке WSDL-атакующих - помечаем как заблокированный из-за WSDL
    if ip in WSDL_ATTACKER_IPS:
        blocked_status.append("ЗАБЛОКИРОВАН")
        blocked_ips.append(ip)
        print(f" {ip}: Отправлен фейковый WSDL (попыток: {protector.attackers_log[ip]})")
    # Проверка на превышение лимита
    elif requests_per_ip[i] > THRESHOLD:
        blocked_status.append("ЗАБЛОКИРОВАН")
        blocked_ips.append(ip)
        print(f"🔒 {ip}: Заблокирован по лимиту ({requests_per_ip[i]} > {THRESHOLD:.0f})")
    else:
        blocked_status.append("РАЗРЕШЕН")
        allowed_ips.append(ip)
        print(f"✅ {ip}: Разрешен ({requests_per_ip[i]} запросов)")

print(f"\nИТОГО:")
print(f"  - Разрешено: {len(allowed_ips)} IP")
print(f"  - Заблокировано: {len(blocked_ips)} IP")
print(f"  - Из них WSDL-атак: {len(wsdl_attack_ips)}")
print(f"  - Выдано фейковых WSDL: {sum(protector.fake_responses.values())}")

# БЛОК 7: ФУНКЦИИ ДЛЯ ДОСТУПА ИЗ VIEWS.PY

def get_fake_wsdl_for_ip(ip_address):
    """Возвращает фейковый WSDL для конкретного IP"""
    if ip_address in protector.attackers_log:
        attempt = protector.attackers_log[ip_address]
        return generate_fake_wsdl(ip_address, attempt)
    return generate_fake_wsdl(ip_address, 1)
# Возвращает фейковый WSDL конкретного IP с учётом числа его попыток
# Чем больше попыток — тем более краткий ответ он получает
def get_attackers_with_fake_wsdl():
    # Собирает и возвращает список словарей для отображения в шаблоне: [{ip, attempts, fake_wsdl, fake_count}]
    attackers_list = []
    for ip in wsdl_attack_ips:
        attackers_list.append({
            'ip': ip,
            'attempts': protector.attackers_log.get(ip, 0),
            'fake_wsdl': get_fake_wsdl_for_ip(ip),
            'fake_count': protector.fake_responses.get(ip, 0)
        })
    return attackers_list

print(f"   Обнаружено WSDL-атак: {len(wsdl_attack_ips)} IP")
print(f"   Заблокировано: {len(blocked_ips)} IP, Разрешено: {len(allowed_ips)} IP")