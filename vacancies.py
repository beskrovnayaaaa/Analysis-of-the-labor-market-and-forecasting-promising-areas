import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import json
# from pprint import pprint


def get_links(text):
    user_agent = fake_useragent.UserAgent()
    data = requests.get(
        url=f"https://hh.ru/search/vacancy?text={text}&items_on_page=20&ored_clusters=true&page=1",
        headers={"user-agent": user_agent.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        page_count = int(
            soup.find("div", attrs={"class": "pager"}).find_all("span", recursive=False)[-1].find("a").find(
                "span").text)
    except:
        return
    for page in range(page_count):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?text={text}&items_on_page=20&ored_clusters=true&page={page}",
                headers={"user-agent": user_agent.random}
            )

            soup = BeautifulSoup(data.content, "lxml")
            link_spans = soup.find_all('span', class_='serp-item__title-link-wrapper')
            for span in link_spans:
                link = span.find('a', class_='bloko-link')
                if link and 'href' in link.attrs:
                    href = link['href']
                    if 'adsrv' not in href:
                        yield f"{href.split('?')[0]}"
        except Exception as e:
            print(f"{e}")


def get_vacancies(link):
    user_agent = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent": user_agent.random}
    )
    if data.status_code != 200:
        return

    soup = BeautifulSoup(data.content, "lxml")

    name = soup.find(attrs={"data-qa": "vacancy-title"})
    name = name.text if name else ""

    salary = soup.find(attrs={"data-qa": "vacancy-salary"})
    salary = salary.text.replace("\xa0000", "") if salary else ""

    required_experience = soup.find(attrs={"data-qa": "vacancy-experience"})
    required_experience = required_experience.text if required_experience else ""

    employment = soup.find(attrs={"data-qa": "vacancy-view-employment-mode"})
    employment = employment.text if employment else ""

    description = soup.find(attrs={"class": "vacancy-description"})
    description = description.text if description else ""

    skills = soup.find_all(attrs={"class": "bloko-tag__section_text"})
    # Список для хранения текстовых данных
    skill_texts = []
    # Перебираем все элементы в списке skills
    for skill in skills:
        # Извлекаем текст из каждого элемента и добавляем его в список skill_texts
        skill_texts.append(skill.text)
    # Преобразуем список текстовых данных в строку, разделяя элементы запятой
    skills_string = ', '.join(skill_texts)

    time_publication = soup.find(attrs={"class": "vacancy-creation-time-redesigned"})
    time_publication = time_publication.text.split('в', maxsplit=3)[1].replace("\xa0", " ").replace("ана", "") if time_publication else ""

    place = soup.find(attrs={"class": "vacancy-creation-time-redesigned"})
    place = place.text.split('в', maxsplit=2)[2] if place else ""


    vacancies = {
        "name": name,
        "salary": salary,
        "required_experience": required_experience,
        "employment": employment,
        "description": description,
        "skills": skills_string,
        "time_publication": time_publication,
        "place": place
    }

    return vacancies


# vacancies_links = get_links("ui+ux")
# for link in vacancies_links:
#     pprint(get_vacancies(link))

if __name__ == "__main__":
    start_time = time.time()
    data = []
    counter = 0
    vacancies_links = get_links("product дизайнер")
    for link in vacancies_links:
        vacancy_data = get_vacancies(link)
        data.append(vacancy_data)
        with open("datav_p.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        counter = counter + 1
        print(f"{counter} resume collected. Time spent: {time.time() - start_time}")
