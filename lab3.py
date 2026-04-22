import matplotlib
matplotlib.use('Agg')
from sympy import *
import matplotlib.pyplot as plt

#Расчёт порога блокировки
R, T, N = symbols("R T N")

BASE_RPS = 120
WINDOW = 60
IPS_COUNT = 40

threshold_expr = (R * T) / N
THRESHOLD = float(threshold_expr.subs({R: BASE_RPS, T: WINDOW, N: IPS_COUNT}))
print(f"Порог блокировки: {THRESHOLD:.0f} запросов за {WINDOW} сек")

#IP-адреса и количество запросов
ip_addresses = [
    "192.165.1.10",
    "192.168.1.11",
    "10.0.0.5",
    "192.168.1.12",
    "172.16.0.3",
    "192.165.1.13",
    "10.0.0.15",
    "192.168.1.14",
    "192.168.1.15",
    "10.0.0.20"
]

requests_per_ip = [
    183,  
    60,   
    190,  
    60,   
    187,  
    49,   
    203,   
    39,   
    60,   
    198   
]

blocked_status = []
blocked_ips = []
allowed_ips = []

for i in range(len(ip_addresses)):
    if requests_per_ip[i] > THRESHOLD:
        blocked_status.append("ЗАБЛОКИРОВАН")
        blocked_ips.append(ip_addresses[i])
    else:
        blocked_status.append("РАЗРЕШЕН")
        allowed_ips.append(ip_addresses[i])


#Таблица с результатами
print("Таблица с результатами")
print("IP-адрес        Запросов/мин   Статус")
for i in range(len(ip_addresses)):
    print(f"{ip_addresses[i]:15} {requests_per_ip[i]:12}   {blocked_status[i]}")

print(f"ИТОГО:")
print(f"  - Разрешено: {len(allowed_ips)} IP")
print(f"  - Заблокировано: {len(blocked_ips)} IP")

print(f"\nЗаблокированные IP (нарушители):")
for ip in blocked_ips:
    print(f"  {ip}")

#Визуализация
#График 13
plt.figure()
colors = ['red' if x == "ЗАБЛОКИРОВАН" else 'green' for x in blocked_status]
plt.bar(ip_addresses, requests_per_ip, color=colors, edgecolor='black')
plt.axhline(y=THRESHOLD, color='red', linestyle='--')
plt.title("Активность IP-адресов")
plt.xlabel("IP-адрес")
plt.ylabel("Запросов в минуту")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart13.png")

#График 14
plt.figure()

allowed_reqs = []
blocked_reqs = []

for i in range(len(ip_addresses)):
    if requests_per_ip[i] <= THRESHOLD:
        allowed_reqs.append(requests_per_ip[i])
    else:
        blocked_reqs.append(requests_per_ip[i])


avg_allowed = sum(allowed_reqs) / len(allowed_reqs)
avg_blocked = sum(blocked_reqs) / len(blocked_reqs)

x = [1, 2]
width = 0.35

plt.bar(x[0], avg_allowed, width, color='green', edgecolor='black')
plt.bar(x[1], avg_blocked, width, color='red', edgecolor='black')
plt.axhline(y=THRESHOLD, color='blue', linestyle='--',)
plt.title("Средняя активность IP-адресов")
plt.xlabel("Статус IP")
plt.ylabel("Запросов в минуту")
plt.xticks(x, ['Разрешённые', 'Заблокированные'])
plt.tight_layout()
plt.savefig("chart14.png")


#График 15
plt.figure()
pie_data = [len(blocked_ips), len(allowed_ips)]
pie_labels = [f"Заблокировано\n{len(blocked_ips)} IP", f"Разрешено\n{len(allowed_ips)} IP"]
pie_colors = ['red', 'green']
plt.pie(pie_data, labels=pie_labels, autopct="%1.0f%%", colors=pie_colors)
plt.title("Статус IP-адресов")
plt.savefig("chart15.png")

#График 16
lam = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200]  
prob = []
for l in lam:
    if l <= THRESHOLD:
        p = (l / THRESHOLD) * 30
    else:
       p = 30 + (l - THRESHOLD) / THRESHOLD * 65 
    if p > 95:
        p = 95
    prob.append(p)

plt.figure()
plt.bar(lam, prob, color='orange', edgecolor='black')
plt.axhline(y=50, color='red', linestyle='--')
plt.title("Вероятность сканирования WSDL в зависимости от интенсивности")
plt.xlabel("Интенсивность запросов (запросов в минуту)")
plt.ylabel("Вероятность превышения порога (%)")
plt.xticks(lam, rotation=45)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig("chart16.png")

#График 17
plt.figure()
if len(blocked_ips) > 0:
    blocked_data = []
    for i in range(len(ip_addresses)):
        if blocked_status[i] == "ЗАБЛОКИРОВАН":
            blocked_data.append((ip_addresses[i], requests_per_ip[i]))

    for i in range(len(blocked_data)):
        for j in range(i+1, len(blocked_data)):
            if blocked_data[j][1] > blocked_data[i][1]:
                blocked_data[i], blocked_data[j] = blocked_data[j], blocked_data[i]

    top_ips = [x[0] for x in blocked_data[:5]]
    top_req = [x[1] for x in blocked_data[:5]]

    plt.barh(top_ips, top_req, color='red')
    plt.axvline(x=THRESHOLD, color='blue', linestyle='--')
    plt.title("Топ нарушителей (заблокированные IP)")
    plt.xlabel("Количество запросов в минуту")
    plt.tight_layout()
plt.savefig("chart17.png")

#График 18
ranges = ['0-30', '31-60', '61-90', '91-120', '121-150', '151+']
counts = [0, 0, 0, 0, 0, 0]

for req in requests_per_ip:
    if req <= 30:
        counts[0] += 1
    elif req <= 60:
        counts[1] += 1
    elif req <= 90:
        counts[2] += 1
    elif req <= 120:
        counts[3] += 1
    elif req <= 150:
        counts[4] += 1
    else:
        counts[5] += 1

plt.figure()
plt.bar(ranges, counts, color='purple', edgecolor='black')
plt.title("Распределение IP по диапазонам активности")
plt.xlabel("Диапазон запросов в минуту")
plt.ylabel("Количество IP")
plt.tight_layout()
plt.savefig("chart18.png")