# Развертывание SFMShop в Kubernetes

## Обзор

Конфигурация для развертывания интернет-магазина SFMShop в Kubernetes.

## Компоненты

- **Deployment** — 3 реплики приложения
- **Service** — LoadBalancer для внешнего доступа

## Быстрый старт

```bash
# Применить конфигурации
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Проверить статус
kubectl get pods -l app=sfmshop
kubectl get svc sfmshop-service
```

## Масштабирование

```bash
# Увеличить до 5 реплик
kubectl scale deployment sfmshop-deployment --replicas=5

# Уменьшить до 2 реплик
kubectl scale deployment sfmshop-deployment --replicas=2
```

## Переменные окружения

| Переменная | Значение |
|------------|----------|
| `DB_HOST` | postgres-service |
| `DB_PORT` | 5432 |
| `DB_NAME` | sfmshop |
| `DB_USER` | postgres |
| `REDIS_URL` | redis://redis-service:6379 |

## Очистка

```bash
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml
```