import json

DEFAULT_SETTINGS = {
    "username": "Пользователь",
    "theme": "dark"
}


def load_settings():
    try:
        with open("settings.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            for key, value in DEFAULT_SETTINGS.items():
                data.setdefault(key, value)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings_data):
    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump(settings_data, file, ensure_ascii=False, indent=4)


def display_settings(settings_data):
    print(f"👤 Имя: {settings_data.get('username', 'Пользователь')}")
    print(f"🎨 Тема: {settings_data.get('theme', 'dark')}")


def settings():
    menu = [
        "  ---⚙️ Настройки---",
        "1. Показать настройки",
        "2. Изменить имя",
        "3. Изменить тему",
        "4. Сбросить настройки",
        "5. Выйти",
    ]

    settings_data = load_settings()

    while True:
        print("\n" + "—" * 20)
        for item in menu:
            print(item)
        print("—" * 20)

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            print("\n⚙️ Текущие настройки:")
            display_settings(settings_data)

        elif choice == "2":
            new_name = input("Введите ваше имя: ").strip()
            if not new_name:
                print("❌ Имя не может быть пустым.")
            else:
                settings_data["username"] = new_name
                save_settings(settings_data)
                print(f"✅ Имя успешно изменено на '{new_name}'!")

        elif choice == "3":
            print("\n🎨 Выберите тему:")
            print("1. 🌙 Тёмная (dark)")
            print("2. ☀️ Светлая (light)")
            theme_choice = input("Ваш выбор: ").strip()

            if theme_choice == "1":
                settings_data["theme"] = "dark"
                save_settings(settings_data)
                print("✅ Тема изменена на 'dark'!")
            elif theme_choice == "2":
                settings_data["theme"] = "light"
                save_settings(settings_data)
                print("✅ Тема изменена на 'light'!")
            else:
                print("❌ Неверный выбор темы.")
        elif choice == "4":
            confirm = input("⚠️ Вы уверены, что хотите сбросить настройки? (да/нет): ").strip().lower()
            if confirm in ["да", "yes", "д", "y"]:
                settings_data = DEFAULT_SETTINGS.copy()
                save_settings(settings_data)
                print("🔄 Настройки успешно сброшены до значений по умолчанию!")
            else:
                print("Отмена сброса настроек.")

        elif choice == "5":
            print("Выход из настроек.")
            break

        else:
            print("❌ Неверный пункт меню!")
if __name__ == "__main__":
    settings()
