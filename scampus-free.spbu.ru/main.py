import requests 
from bs4 import BeautifulSoup
import lxml
from config import *
import csv


params = {
    "RoomSearch[campus_id]": "",
    "RoomSearch[komnata]": "",
    "RoomSearch[svobodno_zhenskih]": "",
    "RoomSearch[svobodno_muzhskih]": "",
    "RoomSearch[Bpolnostju_svobodnyh]": "",
    "RoomSearch[vozmozhno_mest]": "",
    "page": ""
}
url = "https://campus-free.spbu.ru/site/index"

table_headers = ["Общежитие", "Помещение №", "Тип комнаты", "Количество свободных женских мест", "Количество свободных мужских мест", "Количество полностью свободных мест", "Общее количество мест в комнате"]


def main() -> None:
    with open("punk.csv", "w", encoding="utf-8") as file:
        writer =csv.writer(file, lineterminator="\r") 
        writer.writerow(table_headers)
        for key in dorms: 
            print(f"### Processing {key}...")

            params["RoomSearch[campus_id]"] = dorms[key]

            for i in range(1, pages[key]+1):
                print(f"Page: {i}/{pages[key]}")

                params["page"] = i
                resp = requests.get(url=url, headers=headers, params=params)
                data = resp.content.decode("utf-8")
                
                soup = BeautifulSoup(data, "lxml")
                table_body = soup.find("tbody")
                rows = table_body.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    cols = [col.text.strip() for col in cols]
                    cols[0] = cols[0][-2:]
                    cols[1] = cols[1].split(" ")[0]
                    if "а" in cols[1]:
                        cols[1] = str.replace(cols[1], "а", " ")
                        cols.insert(2, "а")
                    elif "б" in cols[1]:
                        cols[1] = str.replace(cols[1], "б", " ")
                        str.replace(cols[1], "б", " ")
                        cols.insert(2, "б")
                    else:
                        cols.insert(2, "-")
                    writer.writerow(cols)   
            

                # if i == 1: break


            # if key == 10: break


if __name__ == "__main__":
    main()
