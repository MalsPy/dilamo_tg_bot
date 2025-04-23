from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Мальчики','Девочки']

description_for_info_pages = {
    "main": "Dilamo kids\nBabyshoppinguz (старый аккаунт )\nДетская одежда из Турции и Китая\n",
    "about": "• Принимаем заказы круглосуточно \n• Самарканд, ул. Узбекистанская (ориентир — 34-я школа)\n• Тел: +998 50 550 33 59\n Instagram:\nhttps://www.instagram.com/dilamikids?igsh=MWNnbTc3ZnFkNDloMw==",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "• Наличными при получении",
        "• Переводом на карту",
        "• Переводом на карту Можно оплатить доставщику или скинуть на карту после получения товара",
        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Доставка по Узбекистану:"),
            "• По Самарканду — TaxiOK, Яндекс, доставщик",
            "• По регионам — почта BTS и EMU",
            marker="✅ ",
        ),
        sep="\n----------------------\n",
    ).as_html(),
    'catalog': 'Категории:',
    'cart': 'В корзине ничего нет!'
}
