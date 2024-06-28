import os
import tarfile

from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from landsatxplore.errors import LandsatxploreError

from gui.gui_utils import (DownloadBarFrame, DownloadProgressBar,
                           InformationTable)


def get_tile_list(satellite_grid, input_shapefile):
    """
    Возвращает список тайлов, которые определяются на основе пересечения входного shapefile и сетки Landsat 8,9.

    :param satellite_grid (GeoDataFrame): Векторный слой сетки Landsat 8,9.
    :param input_shapefile(GeoDataFrame): Векторный слой, для которого нужно определить пересечение с тайлами.

    :return: Список тайлов, которые удовлетворяют условию пересечения входного shapefile и сетки Landsat 8,9.
    """
    # Проверяем, совпадают ли системы координат shapefile и сетки тайлов.
    if input_shapefile.crs != satellite_grid.crs:
        input_shapefile = input_shapefile.to_crs(satellite_grid.crs)

    single_polygon = input_shapefile.geometry.unary_union
    selected_polygons = []

    for index, row in satellite_grid.iterrows():
        if row.geometry.intersects(single_polygon):
            selected_polygons.append(row["Name"].replace("_", "0"))

    return selected_polygons


# Function to log in to Landsat Explorer API
def landsat_explorer_login(username: str, password: str) -> API:
    """
    Устанавливает соединение с API Landsat Explorer.

    :param username: Имя пользователя для аутентификации.
    :param password: Пароль для аутентификации.

    :return: Объект API при успешной аутентификации, иначе None.
    """
    try:
        api = API(username, password)
        print("Соединение с Landsat API установлено.")
        return api
    except LandsatxploreError as e:
        print(f"Произошла ошибка LandsatXPlore во время аутентификации: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

    return None


# Function to log in to Landsat Earth Explorer
def earth_explorer_login(username: str, password: str):
    """
    Устанавливает соединение с API Landsat Earth Explorer.

    :param username: Имя пользователя для аутентификации.
    :param password: Пароль для аутентификации.

    :return: Объект EarthExplorer при успешной аутентификации, иначе None.
    """
    try:
        ee = EarthExplorer(username, password)
        print("Подключение к API Landsat Earth Explorer выполнено.")
        return ee
    except LandsatxploreError as le:
        print(f"Произошла ошибка при подключении к Landsat Earth Explorer: {str(le)}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {str(e)}")

    return None


# Function to search for Landsat images
def landsat_search(
    username: str, password: str, dataset: str, bbox: str, start_date: str, end_date: str, max_cloud_cover: str
):
    """
    Поиск сцен Landsat 8,9, удовлетворяющих заданным условиям.

    :param username (str): Имя пользователя для доступа к Landsat Explorer API.
    :param password (str): Пароль пользователя для доступа к Landsat Explorer API.
    :param dataset (str): Идентификатор набора данных Landsat 8,9.
    :param bbox (str): Географический ограничивающий прямоугольник в формате "min_lon, min_lat, max_lon, max_lat".
    :param start_date (str): Начальная дата поиска в формате "YYYY-mm-dd".
    :param end_date (str): Конечная дата поиска в формате "YYYY-mm-dd".
    :param max_cloud_cover (str): Максимальный процент облачности над тайлом.

    :return: Список сцен Landsat, удовлетворяющих заданным условиям.
    """
    try:
        api = landsat_explorer_login(username, password)
        scenes_landsat = api.search(
            dataset=dataset,
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover=max_cloud_cover,
            max_results=500,
        )
        api.logout()
        if len(scenes_landsat) == 0:
            print("Ни одного продукта не найдено")
        else:
            print(f"Cцен найдено: {len(scenes_landsat)}.")
            return scenes_landsat
    except:
        print("Процесс не может быть выполнен")
        return None


# Function to download Landsat images
def download_landsat_images(
    username, password, qp, satellite_grid, input_shapefile, dir_downld, master_frame, verified_tiles=[]
):
    """
    Загружает изображения Landsat на основе входных параметров.

    :param username (str): Имя пользователя для Earth Explorer.
    :param password (str): Пароль для Earth Explorer.
    :param qp (dict): Словарь с параметрами поиска, включая dataset, bbox, start_date, end_date и max_cloud_cover.
    :param satellite_grid (GeoDataFrame): Векторный слой сетки Landsat 8,9.
    :param input_shapefile (GeoDataFrame): Векторный слой, зоны интересов.
    :param dir_downld (str): Директория для сохранения загруженных изображений.
    :param image_tiles (list): Список изображений, которые уже были загружены.

    :return: Список недавно загруженных тайлов.
    """
    # Поиск Landsat-изображений

    query = landsat_search(
        username, password, qp["dataset"], qp["bbox"], qp["start_date"], qp["end_date"], qp["max_cloud_cover"]
    )
    # Получение списка тайлов, пересекающихся с входным shapefile
    zones = get_tile_list(satellite_grid, input_shapefile)
    print("Зоны, покрывающие область интересов:", ", ".join(map(str, zones)))
    # Use a set for faster lookup
    image_tiles_set = set(verified_tiles)

    data_for_table = [
        [t["display_id"], "необходимо загрузить"]
        for t in query
        if any(zone == t["display_id"][10:16] for zone in zones)
        if t["display_id"] not in image_tiles_set
    ]
    titles = [title for title, _ in data_for_table]

    print(f"Продуктов найдено после фильтрации: {len(titles)}.")

    if not titles:
        print("После фильтра ни одного продукта не найдено")
        return titles
    else:
        information_table = InformationTable(master=master_frame, data=data_for_table)
        # Log in to Landsat Earth Explorer
        ee = earth_explorer_login(username, password)

        for title in titles:
            if title in os.listdir(dir_downld):
                print(f"Фай {title} находится в папке")
                for row_num, row in enumerate(data_for_table):
                    if row[0] == title:
                        # Изменить значение в поле 1 на new_status
                        information_table.insert(row_num, 1, "в папке")
                        break
            else:
                archive_name = title + ".tar"
                if archive_name in os.listdir(dir_downld):
                    os.remove(os.path.join(dir_downld, archive_name))

                print(f"ПРОДУКТ {title} НЕ НАХОДИТСЯ В ЛОКАЛЬНОМ ХРАНИЛИЩЕ. НЕОБХОДИМО ЗАГРУЗИТЬ...")

                try:
                    product = next(product for product in query if product["display_id"] == title)
                    product_id = product["entity_id"]

                    dataset_id_list = ["5e83d14f30ea90a9", "5e83d14fec7cae84", "632210d4770592cf"]
                    id_num = len(dataset_id_list)
                    file_size = None
                    for id_count, dataset_id in enumerate(dataset_id_list):
                        try:
                            EE_DOWNLOAD_URL = f"https://earthexplorer.usgs.gov/download/{dataset_id}/{product_id}/EE"
                            filename, file_size = ee._get_fileinfo(EE_DOWNLOAD_URL, timeout=120, output_dir=dir_downld)
                            break
                        except:
                            if id_count + 1 < id_num:
                                pass
                    final_file_size = file_size
                    download_location = os.path.join(dir_downld, archive_name)
                    download_barr = DownloadBarFrame(master=master_frame)
                    for row_num, row in enumerate(data_for_table):
                        if row[0] == title:
                            # Изменить значение в поле 1 на new_status
                            information_table.insert(row_num, 1, "загрузка...")
                            break
                    DownloadProgressBar(download_barr.download_barr_frame, download_location, final_file_size)
                    ee.download(identifier=product_id, output_dir=dir_downld, dataset=qp["dataset"])
                    print(f"Продукт Landsat: {title} загружено!")
                    for row_num, row in enumerate(data_for_table):
                        if row[0] == title:
                            # Изменить значение в поле 1 на new_status
                            information_table.insert(row_num, 1, "загружено!")
                            break

                    with tarfile.open(download_location, "r") as zip_ref:
                        zip_ref.extractall(os.path.join(dir_downld, title))
                    os.remove(download_location)
                    for row_num, row in enumerate(data_for_table):
                        if row[0] == title:
                            # Изменить значение в поле 1 на new_status
                            information_table.insert(row_num, 1, "загружено и разархивировано!")
                            break
                except Exception as e:
                    print(f"Ошибка при загрузке и извлечении {title}: {e}")
                    titles.remove(title)
                    for row_num, row in enumerate(data_for_table):
                        if row[0] == title:
                            # Изменить значение в поле 1 на new_status
                            information_table.insert(row_num, 1, "ошибка")
                            break

        print(f"Продуктов загружено: {len(titles)}.")
        return titles
