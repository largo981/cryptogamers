import json

def filter_games(data):
    filtered_games = []
    
    for segment in data.get("segments", []):
        for game in segment.get("hits", []):
            # Преобразование значений Width и Height в целые числа, если они строки
            try:
                width = int(game.get("Width", 0))
                height = int(game.get("Height", 0))
            except ValueError:
                # Если не удается преобразовать, пропускаем эту игру
                continue
            
            # Условие: ширина меньше высоты
            if width < height:
                # Найти ссылку на изображение 512x512
                assets = game.get("Assets", [])
                image_512x512 = next((url for url in assets if "512x512" in url), None)
                
                if image_512x512:
                    filtered_game = {
                        "Id": game.get("Id"),
                        "Title": game.get("Title"),
                        "Game URL": game.get("Game URL"),
                        
                        "Asset 512x512": image_512x512
                    }
                    filtered_games.append(filtered_game)
    
    return filtered_games

def main():
    input_filename = 'Wizard_Data.json'
    output_filename = 'update.json'

    # Чтение исходного JSON файла с кодировкой utf-8
    with open(input_filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Фильтрация игр
    filtered_data = filter_games(data)

    # Запись результата в новый JSON файл с кодировкой utf-8
    with open(output_filename, 'w', encoding='utf-8') as file:
        json.dump(filtered_data, file, indent=4)

    print(f"Фильтрованные данные сохранены в файл {output_filename}")

if __name__ == "__main__":
    main()
