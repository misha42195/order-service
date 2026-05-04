# Руководство по работе с Kubernetes

## Содержание

1. [Что такое Kubernetes](#что-такое-kubernetes)
2. [Установка](#установка)
3. [Основные понятия](#основные-понятия)
4. [Пошаговое развертывание](#пошаговое-развертывание)
5. [Диагностика проблем](#диагностика-проблем)
6. [Масштабирование](#масштабирование)
7. [Обновление приложения](#обновление-приложения)
8. [Очистка](#очистка)

---

## Что такое Kubernetes

Kubernetes (K8s) — это система для автоматического развертывания, масштабирования и управления контейнеризированными приложениями.

**Основные возможности:**
- Автоматическое распределение нагрузки
- Самовосстановление (перезапуск упавших pod'ов)
- Горизонтальное масштабирование
- Обновление без простоя

---

## Установка

### MiniKube (рекомендуется для обучения)

```bash
# Установить kubectl
sudo apt-get update
sudo apt-get install -y kubectl

# Установить MiniKube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Запустить кластер
minikube start --driver=docker

# Проверить
kubectl get nodes
```

### Docker Desktop (альтернатива)

```bash
# Включить Kubernetes в настройках Docker Desktop
# После включения kubectl настроится автоматически
```

### Kind (ещё один вариант)

```bash
# Установить Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/

# Создать кластер
kind create cluster --name sfmshop
```

---

## Основные понятия

### Pod

**Pod** — минимальная единица в Kubernetes. Это один или несколько контейнеров, которые работают вместе.

```
Pod = один или несколько контейнеров + общий IP + общее хранилище
```

### Deployment

**Deployment** — управляет подами, обеспечивает заданное количество реплик, обновления.

```
Deployment → создаёт → ReplicaSet → создаёт → Pods
```

### Service

**Service** — стабильная точка доступа к подам (не меняется при перезапуске).

```
Service → LoadBalancer → Pods
```

### Namespace

**Namespace** — изоляция ресурсов (можно иметь несколько "сред" в одном кластере).

---

## Пошаговое развертывание

### Шаг 1: Проверить кластер

```bash
# Посмотреть ноды
kubectl get nodes

# Посмотреть все поды (все namespaces)
kubectl get pods --all-namespaces

# Короткий статус
kubectl cluster-info
```

**Ожидаемый вывод:**
```
NAME             STATUS   ROLES           AGE   VERSION
minikube         Ready    control-plane   5d    v1.28.0
```

### Шаг 2: Применить Deployment

```bash
# Из директории проекта
cd /home/misha/PycharmProjects/SFMShop/main-service_clode

# Применить deployment
kubectl apply -f k8s/deployment.yaml

# Проверить
kubectl get deployments
```

**Что происходит:**
1. Kubernetes создаёт Deployment
2. Deployment создаёт ReplicaSet
3. ReplicaSet создаёт 3 Pod'а

### Шаг 3: Применить Service

```bash
# Применить service
kubectl apply -f k8s/service.yaml

# Проверить
kubectl get services
```

### Шаг 4: Проверить статус

```bash
# Все поды
kubectl get pods

# Подробная информация
kubectl get pods -o wide

# Сервисы
kubectl get svc
```

**Пример вывода:**
```
NAME                TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
sfmshop-service     LoadBalancer   10.96.234.115   <pending>     80:30001/TCP   5m
```

### Шаг 5: Доступ к приложению

**Для MiniKube:**
```bash
# Получить URL сервиса
minikube service sfmshop-service --url

# Или просто (откроет в браузере)
minikube service sfmshop-service
```

**Для Docker Desktop:**
```bash
# IP кластера
kubectl cluster-info

# Сервис доступен по localhost:PORT (смотри в kubectl get svc)
```

---

## Диагностика проблем

### Если Pod не запускается

```bash
# 1. Посмотреть статус всех подов
kubectl get pods

# STATUS = Pending — проблема с ресурсами или scheduling
# STATUS = ImagePullBackOff — не может скачать образ
# STATUS = CrashLoopBackOff — контейнер падает
# STATUS = Error — ошибка в контейнере

# 2. Подробности о проблеме
kubectl describe pod <имя пода>

# 3. Логи контейнера
kubectl logs <имя пода>

# 4. Логи всех контейнеров в pod'е (если их несколько)
kubectl logs <имя пода> --all-containers=true
```

### Если Service не работает

```bash
# 1. Проверить endpoints (должны быть IP подов)
kubectl get endpoints sfmshop-service

# 2. Проверить selector (какие pod'ы подключены)
kubectl describe service sfmshop-service

# 3. Тестирование внутри кластера
kubectl run test --image=curlimages/curl --rm -it -- sh
# curl http://sfmshop-service
```

### Полезные команды диагностики

```bash
# Все события кластера ( newest first)
kubectl get events --sort-by='.lastTimestamp'

# Все ресурсы в namespace default
kubectl get all

# Проверить конфигурацию
kubectl explain deployment
kubectl explain service
```

---

## Масштабирование

### Изменить количество реплик

```bash
# Увеличить до 5
kubectl scale deployment sfmshop-deployment --replicas=5

# Уменьшить до 2
kubectl scale deployment sfmshop-deployment --replicas=2

# Проверить
kubectl get pods
```

### Автоматическое масштабирование (HPA)

```bash
# Создать autoscaler
kubectl autoscale deployment sfmshop-deployment \
  --min=2 --max=10 --cpu-percent=70

# Посмотреть
kubectl get hpa

# Удалить
kubectl delete hpa sfmshop-deployment
```

---

## Обновление приложения

### Обновить образ

```bash
# Изменить версию образа в deployment
# Например, изменить image: sfmshop:latest на image: sfmshop:v2

# Применить изменения
kubectl apply -f k8s/deployment.yaml

# Или одной командой
kubectl set image deployment/sfmshop-deployment sfmshop=sfmshop:v2
```

### Отслеживание обновления

```bash
# Статус rollout
kubectl rollout status deployment/sfmshop-deployment

# История rollout'ов
kubectl rollout history deployment/sfmshop-deployment
```

### Откат

```bash
# Откатить к предыдущей версии
kubectl rollout undo deployment/sfmshop-deployment

# Откатить к конкретной ревизии
kubectl rollout undo deployment/sfmshop-deployment --to-revision=2
```

---

## Очистка

```bash
# Удалить deployment
kubectl delete -f k8s/deployment.yaml

# Удалить service
kubectl delete -f k8s/service.yaml

# Удалить всё одной командой
kubectl delete -f k8s/

# Удалить кластер MiniKube
minikube delete
```

---

## Полезные команды (шпаргалка)

```bash
# === Pods ===
kubectl get pods                    # Список pod'ов
kubectl describe pod <name>         # Информация о pod'е
kubectl logs <name>                 # Логи
kubectl exec -it <name> -- sh       # Войти в контейнер

# === Deployments ===
kubectl get deployments             # Список deployments
kubectl apply -f <file>            # Применить конфигурацию
kubectl scale --replicas=5         # Масштабировать

# === Services ===
kubectl get services                # Список сервисов
kubectl describe service <name>    # Информация о сервисе

# === Смотреть всё ===
kubectl get all                     # Все ресурсы
kubectl get events                 # События кластера

# === Отладка ===
kubectl diff -f <file>             # Посмотреть изменения
kubectl rollout status             # Статус обновления
```

---

## Пример рабочего процесса

```bash
# 1. Запуск кластера
minikube start

# 2. Развертывание
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 3. Проверка
kubectl get pods
# STATUS должен быть Running для всех 3 pod'ов

# 4. Получить URL
minikube service sfmshop-service --url

# 5. Тестирование
curl <полученный URL>/api/v1/products

# 6. Диагностика (если что-то не работает)
kubectl describe pod <имя>
kubectl logs <имя>

# 7. Очистка
kubectl delete -f k8s/
```

---

## Дополнительные ресурсы

- [Официальная документация Kubernetes](https://kubernetes.io/docs/)
- [kubectl шпаргалка](https://kubernetes.io/docs/reference/kubectl/quick-reference/)
- [MiniKube документация](https://minikube.sigs.k8s.io/docs/)
