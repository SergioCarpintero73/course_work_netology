import requests
from pprint import pprint
import json
from pathlib import Path


class User:
    def __init__(self, vk_token, Ya_token):
        self.vk_token = vk_token
        self.Ya_token = Ya_token

    def get_users_photos(self, user_id):
        url = 'https://api.vk.com/method/photos.get'

        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'access_token': self.vk_token,
            'extended': 1,
            'v': '5.131'
        }
        res = (requests.get(url, params)).json()
        with open('photos_list.json', 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=4)

        photos_info = res['response']['items']
        dict_for_upload = {}
        for photo_data in photos_info:
            file_name = str(photo_data['likes']['count']) + '.jpg'
            print(file_name)
            file_link = photo_data['sizes'][-1]
            print(file_link)
            if file_name in dict_for_upload.keys():
                file_name_new = str(photo_data['likes']['count']) + '_' + str(photo_data['date']) + '.jpg'
                dict_for_upload[file_name_new] = file_link['url']
            else:
                dict_for_upload[file_name] = file_link['url']
            print(dict_for_upload)

        with open('photo_list_upload.json', 'w', encoding='utf-8') as f:
            json.dump(dict_for_upload, f, ensure_ascii=False, indent=4)
        return dict_for_upload

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.Ya_token),
            'Accept': 'application/json'
        }

    def create_file_for_photo(self, folder_name):
        params = {
            "path": folder_name
        }
        respond = requests.put(
            'https://cloud-api.yandex.net/v1/disk/resources',
            headers=self.get_headers(),
            params=params
        )
        return respond

    def upload_users_photo(self, folder_name):
        with open("photo_list_upload.json") as f:
            data = json.load(f)
        for file_name, file_path in data.items():
            path_to_disk = str(folder_name) + '/' + file_name
            url_for_load = file_path
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = self.get_headers()
            params = {
                "url": url_for_load,
                "path": path_to_disk,
                "disable_redirects": "true"
            }
            response = requests.post(url, headers=headers, params=params)
            response.raise_for_status()
            upload_url = (response.json()).get("href", "")
            status = requests.get(upload_url, headers=headers)
            pprint(status.json())
        print('Загрузка успешно завершена')


if __name__ == '__main__':
    my_file = Path('vk_token.txt')
    my_file_2 = Path('Ya_token.txt')
    if my_file.is_file() and my_file_2.is_file():
        with open('vk_token.txt', 'r') as file_object:
            vk_token = file_object.read().strip()
        with open('Ya_token.txt', 'r') as file_object:
            Ya_token = file_object.read().strip()
        begemot_korovin = User(vk_token, Ya_token)
        print('Добрый день! /n Если вы желаете скачать фото из профил вк на Яндекс диск, наберите "Да" ')
        getting_agreement = input().islower()
        if getting_agreement == 'lf' or 'да':
            Vk_id = int(input('Введите ID VK профиля для скачивания фото: '))
            folder_name = str(input('Введите имя папки для сохранения фото'))
            begemot_korovin = User(vk_token, Ya_token)
            try:
                begemot_korovin.get_users_photos(Vk_id)
                begemot_korovin.create_file_for_photo(folder_name)
                begemot_korovin.upload_users_photo(folder_name)
            except KeyError as e:
                print('Возникла ошибка, проверьте правильность токенов доступа')

        else:
            print('До свидания')
            exit()
    else:
        print(f'Создайте 2 отдельных файла в формате .txt с именами {my_file} и {my_file_2} в корневой папке проекта')