# БЛОК 1: ИМПОРТЫ
from django.shortcuts import render
from django.http import HttpResponse # Используется для отдачи файла на скачивание
from lab3 import (
    ip_addresses, requests_per_ip, THRESHOLD, blocked_status, 
    blocked_ips, allowed_ips, wsdl_attack_ips, fake_wsdl_sent_ips,
    protector, get_fake_wsdl_for_ip, get_attackers_with_fake_wsdl
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


def index(request):
    """Главная страница со статистикой и графиками"""

    # Формируем список IP для таблицы
    ip_status_list = []
    for i in range(len(ip_addresses)):
        ip_status_list.append({
            'address': ip_addresses[i],
            'requests': requests_per_ip[i],
            'status': blocked_status[i],
            'is_wsdl_attack': ip_addresses[i] in wsdl_attack_ips,
            'fake_wsdl_sent': ip_addresses[i] in fake_wsdl_sent_ips
        })

    # ГРАФИК 13
    plt.figure(figsize=(10, 6))
    colors = []
    for i, ip in enumerate(ip_addresses):
        if blocked_status[i] == "РАЗРЕШЕН":
            colors.append('green')
        elif ip in wsdl_attack_ips:
            colors.append('darkred')
        else:
            colors.append('red')

    plt.bar(ip_addresses, requests_per_ip, color=colors, edgecolor='black')
    plt.axhline(y=THRESHOLD, color='blue', linestyle='--', label=f'Порог: {THRESHOLD:.0f}')
    plt.title("Активность IP-адресов (темно-красный - WSDL-сканирование)")
    plt.xlabel("IP-адрес")
    plt.ylabel("Запросов в минуту")
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart13 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    # ГРАФИК 15 - Круговая диаграмма
    plt.figure(figsize=(8, 8))
    regular_blocked = len(blocked_ips) - len(wsdl_attack_ips)
    pie_data = [len(allowed_ips), regular_blocked, len(wsdl_attack_ips)]
    pie_labels = [
        f"Разрешено\n{len(allowed_ips)} IP",
        f"Заблокировано (лимит)\n{regular_blocked} IP",
        f"Заблокировано (WSDL)\n{len(wsdl_attack_ips)} IP"
    ]
    pie_colors = ['green', 'red', 'darkred']
    plt.pie(pie_data, labels=pie_labels, autopct="%1.0f%%", colors=pie_colors)
    plt.title("Статус IP-адресов (с разделением по типу угрозы)")
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart15 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    # ГРАФИК 19 - WSDL-атаки
    chart19 = ""
    if len(wsdl_attack_ips) > 0:
        plt.figure(figsize=(10, 6))
        wsdl_counts = [protector.attackers_log.get(ip, 0) for ip in wsdl_attack_ips]
        bars = plt.bar(wsdl_attack_ips, wsdl_counts, color='orange', edgecolor='black')
        plt.title(f"WSDL-сканирования по IP (всего: {len(protector.wsdl_attacks)} попыток)")
        plt.xlabel("IP-адрес")
        plt.ylabel("Количество попыток WSDL-запросов")
        plt.xticks(rotation=45, ha='right')
        for bar, count in zip(bars, wsdl_counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                     str(count), ha='center', va='bottom')
        plt.tight_layout()
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart19 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

    # Детали WSDL-атак
    wsdl_attacks_detail = []
    if protector and hasattr(protector, 'wsdl_attacks'):
        for attack in protector.wsdl_attacks[-10:]:
            wsdl_attacks_detail.append({
                'ip': attack['ip'],
                'timestamp': attack['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'attempt': attack['attempt'],
                'url': attack['url']
            })

    context = {
        'ip_status_list': ip_status_list,
        'threshold': round(THRESHOLD, 0),
        'blocked_count': len(blocked_ips),
        'allowed_count': len(allowed_ips),
        'wsdl_attacks_count': len(wsdl_attack_ips),
        'fake_wsdl_sent': sum(protector.fake_responses.values()),
        'chart13': chart13,
        'chart15': chart15,
        'chart19': chart19,
        'wsdl_attacks_detail': wsdl_attacks_detail,
    }

    return render(request, 'index.html', context)


def fake_wsdl_viewer(request):
    """Страница просмотра фейковых WSDL-ответов"""

    # Получаем список атакующих
    attackers = get_attackers_with_fake_wsdl()

    # Получаем выбранный IP
    selected_ip = request.GET.get('ip', None)
    selected_wsdl = None
    selected_attempts = None

    if selected_ip:
        for attacker in attackers:
            if attacker['ip'] == selected_ip:
                selected_wsdl = attacker['fake_wsdl']
                selected_attempts = attacker['attempts']
                break

    # Если нет выбранного IP и есть атакующие - выбираем первого
    if not selected_wsdl and attackers:
        selected_ip = attackers[0]['ip']
        selected_wsdl = attackers[0]['fake_wsdl']
        selected_attempts = attackers[0]['attempts']

    context = {
        'attackers': attackers,
        'total_attacks': len(attackers),
        'total_fake_wsdl_sent': sum(a['fake_count'] for a in attackers),
        'selected_ip': selected_ip,
        'selected_wsdl': selected_wsdl,
        'selected_attempts': selected_attempts,
    }

    return render(request, 'fake_wsdl_viewer.html', context)


def download_fake_wsdl(request, ip_address):
    """Скачивание фейкового WSDL для IP"""
    fake_wsdl = get_fake_wsdl_for_ip(ip_address)
    response = HttpResponse(fake_wsdl, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="fake_wsdl_{ip_address}.xml"'
    return response