import os
import re
import cv2
import easyocr
from ultralytics import YOLO
import requests
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.conf import settings
import numpy as np
from django.core.files.storage import default_storage

site_url = "https://www.keralalotteriesresults.in/"
MODEL_PATH = os.path.join(settings.BASE_DIR, "home", "best.pt")


def check_result(n, results):
    for i in results.keys():
        if n in results[i]:
            return f"🎉 Congratulations! Your number {n} has won the {i} 🎊"

        if n[-4:] in results[i]:
            return f"🌟 Great news! Your last four digits match the {i}: {n}"

    return "Better luck next time"


def index(request):
    return render(request, "index.html")


def second(request):
    n = None
    if request.method == "POST":
        lottery_name = request.POST.get("lottery")
        lottery_image = request.FILES.get("image")

        if not lottery_image:
            return render(request, "second.html", {"error": "Please upload an image."})

        # Save the uploaded image
        image_path = default_storage.save(lottery_image.name, lottery_image)
        image_path = os.path.join(settings.MEDIA_ROOT, image_path)

        # Fetch the latest lottery results
        response = requests.get(site_url)
        if response.status_code != 200:
            return render(request, "second.html", {"error": "Could not fetch lottery results."})

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        url = None
        for link in links:
            if f"{lottery_name.upper()} Lottery" in link.text:
                url = link["href"]
                break

        if not url:
            return render(request, "second.html", {"error": f"Could not find results for {lottery_name}."})

        lottery_response = requests.get(url)
        if lottery_response.status_code != 200:
            return render(request, "second.html", {"error": "Failed to retrieve lottery results."})

        soup = BeautifulSoup(lottery_response.text, "html.parser")
        content = soup.get_text(separator="\n", strip=True)

        start_index = content.find("1st Prize")
        if start_index == -1:
            return render(request, "second.html", {"error": "Lottery results not found."})

        lottery_results = content[start_index:]
        prizes = {}

        for prize_level in ["1st", "2nd"]:
            match = re.search(rf"{prize_level} Prize.*?\n([A-Z]+\s\d+)", lottery_results)
            prizes[prize_level] = match.group(1) if match else "Not Available"

        consolation_match = re.search(r"Consolation Prize.*?\n([\w\s]+)", lottery_results, re.MULTILINE)
        if consolation_match:
            consolation_numbers = re.findall(r"([A-Z]+\s\d+)", consolation_match.group(1))
            prizes["Consolation"] = consolation_numbers if consolation_numbers else "Not Available"
        else:
            prizes["Consolation"] = "Not Available"

        third_prize_match = re.search(r"3rd Prize.*?\n([\w\s\(\)-]+)", lottery_results, re.MULTILINE)
        if third_prize_match:
            third_prize_text = third_prize_match.group(1)
            third_prize_numbers = re.findall(r"[A-Z]{2}\s\d{6}", third_prize_text)

            if not third_prize_numbers:
                third_prize_numbers = re.findall(r"\b\d{4}\b", third_prize_text)

            prizes["3rd Prize"] = third_prize_numbers if third_prize_numbers else "Not Available"
        else:
            prizes["3rd Prize"] = "Not Available"

        for i in range(4, 9):
            prize_match = re.search(rf"{i}[a-zA-Z]* Prize.*?\n([\d\s]+?)(?:\n\d|$)", lottery_results, re.MULTILINE)
            if prize_match:
                numbers = prize_match.group(1).strip().split()
                numbers = [num for num in numbers if len(num) >= 3]
                prizes[f"{i}th Prize"] = numbers if numbers else "Not Available"
            else:
                prizes[f"{i}th Prize"] = "Not Available"

        model = YOLO(MODEL_PATH)

        image = cv2.imread(image_path)
        reader = easyocr.Reader(["en"])
        results = model(image)

        lottery_number = None
        for result in results:
            for box in result.boxes.xyxy:
                x1, y1, x2, y2 = map(int, box)
                roi = image[y1:y2, x1:x2]
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                extracted_text = reader.readtext(gray_roi, detail=0)
                if extracted_text:
                    lottery_number = " ".join(extracted_text).strip()
                    break

        if not lottery_number:
            return render(request, "second.html", {"error": "Failed to extract lottery number from image."})
        
        print(lottery_number)

        n = check_result(lottery_number, prizes)
        

    return render(request, "second.html", {"result": n})
