from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Детская одежда']

description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": "Режим работы - круглосуточно.",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении карта/кеш",
        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Варианты доставки/заказа:"),
            "Курьер",
            "Самовынос",
            "UzPost",
            marker="✅ ",
        ),
        sep="\n----------------------\n",
    ).as_html(),
    'catalog': 'Категории:',
    'cart': 'В корзине ничего нет!'
}
