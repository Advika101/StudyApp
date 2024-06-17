import google.generativeai as genai
import pathlib
import os
from dotenv import load_dotenv
import PIL.Image
import tqdm
from IPython.display import display
import datetime


load_dotenv()
# check if poppler-utils is installed
os.system("apt-get install poppler-utils")

chapters = 3
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def setup_model():

    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

    if pathlib.Path('textbook').exists():
        pdf_files = pathlib.Path("textbook").glob("*.pdf")
    else:
        print("No PDF files found in the 'textbook' directory. Upload them and try again.")
        exit()

    if pathlib.Path('output').exists():
        os.system("rm -rf output")
    os.mkdir("output")

    #take 1st n chapters
    pdf_files = list(pdf_files)
    pdf_files.sort()
    pdf_files = pdf_files[:chapters]

    for i in range(len(pdf_files)):
        os.mkdir(f"output/chapter-{i}")
        os.system(f"pdftoppm {pdf_files[i]} output/chapter-{i}/images -jpeg")
    print(os.listdir("output"))

    for i in range(len(pdf_files)):
        img = PIL.Image.open(f"output/chapter-{i}/images-01.jpg")
        img.thumbnail([600, 600])
        display(img)

    for i in range(len(pdf_files)):
        pages_in_chapter = len(list(pathlib.Path(f"output/chapter-{i}").glob("*.jpg")))
        path = str(pdf_files[i])[:-4]
        for page in range(1,pages_in_chapter+1):
            page_number = f"{page:02d}"
            os.system(f"pdftotext  {pdf_files[i]} -f {page_number} -l {page_number}")
            os.system(f"mv {path}.txt output/chapter-{i}/text-{page_number}.txt")

    os.system("cat output/chapter-0/text-01.txt")


    files = []
    for i in range(len(pdf_files)):
        image_files = list(pathlib.Path(f"output/chapter-{i}").glob('images-*.jpg'))
        for img in tqdm.tqdm(image_files):
            files.append(genai.upload_file(img))

    texts = []
    for i in range(len(pdf_files)):
        chap_text = [t.read_text() for t in pathlib.Path(f"output/chapter-{i}").glob('text-*.txt')]
        texts.append(chap_text)

    textbook = []
    for page, (text, image) in enumerate(zip(texts, files)):
        textbook.append(f'## Page {page} ##')
        textbook.append(''.join(text))
        textbook.append(image)

    start_date=datetime.date.today()+datetime.timedelta(days=1)
    exam_date = datetime.date(2024, 7, 1)

    response = model.generate_content(
        [f'# I have an exam {exam_date} and need to study these 3 chapters from the science textbook for my science test. Here is the textbook:']+
        textbook +
        [f"""
        [END]\n\nMake a detailed study schedule for the next month.
        Include dates and time slots and the topics I have to study in those time slots.
        Space it out evenly from tomorrow ({start_date}) to {exam_date} so that I cover everything.
        I can study for an hour everyday on the weekdays after school (between 5-9pm).
        I can study for 2 hours on the weekend (anytime between 9am - 7pm) but I prefer sometime before 12pm.
        My timezone is Asia/Kolkata.
        I want to integrate this plan with my Google Calendar. Give me my schedule in JSON format so that I can use it in
        the API.
        Mention ONLY the JSON and nothing else in the response.
        Return response in JSON format.
        """]
    )

    print(response.text)

    return response.text


