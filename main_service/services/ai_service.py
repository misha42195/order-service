import openai

from core.config import settings

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key=settings.ANTHROPIC_API_KEY,
)


def generate_product_description(
    name: str,
    category: str,
    price: float,
) -> str:
    """Генерация описания товара через локальную модель Qwen"""
    response = client.chat.completions.create(
        model="qwen2.5-coder:7b",  # Твоя модель
        messages=[
            {
                "role": "user",
                "content": (
                    f"Напиши короткое описание товара "
                    f"для интернет магазина электроники\n"
                    f"Название: {name}\n"
                    f"Категория: {category}\n"
                    f"Цена: {price} руб.\n"
                    f"2-3 предложения, без воды."
                ),
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # Убедись, что сделал в терминале: ollama run qwen2.5-coder:7b
    print(
        generate_product_description(
            name="Игровой монитор",
            category="Электроника",
            price=25000,
        )
    )
    print(
        generate_product_description(
            name="попугай",
            category="домашнее животное",
            price=25,
        )
    )
