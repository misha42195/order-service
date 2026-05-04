import time
import requests


def diagnose_page_loading(url):
    """Диагностика процесса загрузки страницы"""
    results = {}

    # 1. Измерение DNS запроса
    import socket

    # измерение времени получения ip
    start = time.time()
    hostname = url.split("/")[2]
    ip = socket.gethostbyname(hostname)
    dns_time = time.time() - start
    results["dns"] = dns_time

    # 2. Измерение времени подключения
    # измеряем время получения ответа по запросу
    start = time.time()
    response = requests.get(url)
    total_time = time.time() - start
    results["total"] = total_time

    # 3. Анализ времени ответа сервера
    server_time = response.elapsed.total_seconds()
    results["server"] = server_time

    # 4. Размер ответа
    results["size"] = len(response.content)

    return results


# Использование
url = "https://sfmshop.com/api/products"
diagnostics = diagnose_page_loading(url)
print(f"DNS: {diagnostics['dns']}  сек")
print(f"Сервер: {diagnostics['server']}  сек")
print(f"Всего: {diagnostics['total']}  сек")
print(f"Размер: {diagnostics['size']}  байты")
