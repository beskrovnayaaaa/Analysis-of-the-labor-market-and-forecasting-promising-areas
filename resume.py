import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import json
# from pprint import pprint


def get_links(text):
    user_agent = fake_useragent.UserAgent()
    data = requests.get(
        url=f"https://hh.ru/search/resume?ored_clusters=true&order_by=relevance&search_period=0&logic=normal&pos=full_text&exp_period=all_time&filter_exp_period=all_time&relocation=living_or_relocation&gender=unknown&professional_role=34&professional_role=25&text={text}&page=1",
        headers={"user-agent": user_agent.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    try:
        page_count = int(soup.find("div", attrs={"class": "pager"}).find_all("span", recursive=False)[-1].find("a").find("span").text)
    except:
        return
    for page in range(page_count):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/resume?ored_clusters=true&order_by=relevance&search_period=0&logic=normal&pos=full_text&exp_period=all_time&filter_exp_period=all_time&relocation=living_or_relocation&gender=unknown&professional_role=34&professional_role=25&text={text}&page={page}",
                headers={"user-agent": user_agent.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, "lxml")
            for a in soup.find_all("a", attrs={"data-qa":"serp-item__title"}):
                print(f'I got a link {a}')
                time.sleep(1)
                yield f"https://hh.ru{a.attrs['href'].split('?')[0]}"
        except Exception as e:
            print(f"{e}")


def get_resume(link):
    user_agent = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent": user_agent.random}
    )
    if data.status_code != 200:
        return

    soup = BeautifulSoup(data.content, "lxml")
    
    name = soup.find(attrs={"class": "resume-block__title-text"})
    name = name.text if name else ""

    gender = soup.find(attrs={"data-qa": "resume-personal-gender"})
    gender = gender.text if gender else ""

    age_element = soup.find(attrs={"data-qa": "resume-personal-age"})
    age = int(age_element.text.replace("\xa0years", "").replace("\xa0year", "").replace("\xa0лет", "").replace("\xa0года","").replace("\xa0год", "")) if age_element else ""

    place_element = soup.find(attrs={"class": "bloko-translate-guard"})
    first_word_place = place_element.text.split(',')[0] if place_element else ""

    salary = soup.find(attrs={"class": "resume-block__salary"})
    salary = salary.text.replace("\u2009", "").replace("\xa0", "").replace("in hand", "").replace("на", "").replace("\xa0", "").replace("руки", "") if salary else ""

    employment = soup.find("div", attrs={"class": "resume-block-item-gap"})
    employment = employment.find("p").text.replace("Employment: ", "").replace("Занятость: ", "") if employment else ""

    experience = soup.find("div", attrs={"data-qa": "resume-block-experience"})
    experience = experience.find("h2").text.replace("Work experience ", "").replace("Опыт работы ", "").replace("\xa0", " ") if experience else ""

    education = soup.find("div", attrs={"data-qa": "resume-block-education"})
    education = education.find("span").text if education else ""

    tags = [tag.text for tag in soup.find(attrs={"class": "bloko-tag-list"}).find_all(attrs={"class": "bloko-tag__section_text"})] if soup.find(attrs={"class": "bloko-tag-list"}) else []

    resume = {
        "name": name,
        "gender": gender,
        "age": age,
        "place": first_word_place,
        "salary": salary,
        "employment": employment,
        "experience": experience,
        "education": education,
        "tags": tags
    }

    return resume


if __name__ == "__main__":
    start_time = time.time()
    #for a in get_links("designer"):
        #pprint(get_resume(a))
    data = []
    counter = 0
    for a in get_links("Дизайнер"):
        data.append(get_resume(a))
        with open("dataset.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        counter = counter + 1
        print(f"{counter} resume collected. Time spent: {time.time() - start_time}")