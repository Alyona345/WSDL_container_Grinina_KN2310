from django.shortcuts import render
from lab3 import ip_addresses, requests_per_ip, THRESHOLD, blocked_status, blocked_ips, allowed_ips
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64

def index(request):
    # Формируем список IP для таблицы
    ip_status_list = []
    for i in range(len(ip_addresses)):
        ip_status_list.append({
            'address': ip_addresses[i],
            'requests': requests_per_ip[i],
            'status': blocked_status[i],
        })

    # ГРАФИК 13 - Активность IP-адресов
    plt.figure(figsize=(10, 6))
    colors = ['red' if x == "ЗАБЛОКИРОВАН" else 'green' for x in blocked_status]
    plt.bar(ip_addresses, requests_per_ip, color=colors, edgecolor='black')
    plt.axhline(y=THRESHOLD, color='red', linestyle='--', label=f'Порог: {THRESHOLD:.0f}')
    plt.title("Активность IP-адресов")
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
    plt.figure(figsize=(8, 6))
    pie_data = [len(blocked_ips), len(allowed_ips)]
    pie_labels = [f"Заблокировано\n{len(blocked_ips)} IP", f"Разрешено\n{len(allowed_ips)} IP"]
    pie_colors = ['red', 'green']
    plt.pie(pie_data, labels=pie_labels, autopct="%1.0f%%", colors=pie_colors)
    plt.title("Статус IP-адресов")
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart15 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    context = {
        'ip_status_list': ip_status_list,
        'threshold': round(THRESHOLD, 0),
        'blocked_count': len(blocked_ips),
        'allowed_count': len(allowed_ips),
        'chart13': chart13,
        'chart15': chart15,
    }

    return render(request, 'index.html', context)
