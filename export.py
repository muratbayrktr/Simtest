import export_csv
import csv
import pandas as pd
import sys
import os
from PIL import Image
from tqdm import tqdm

from fpdf import FPDF
from typing import List
from datetime import datetime
from src._slackbot import SlackOptimizationReportBot


BY = "Performance"
TOP_N = 5
CRITERION = {
    "ROI%": 0.5,
    "Profit Factor": 1.2,
    "Stop Loss": 0
}
COLS = ["name","Performance","Profit Factor","ROI%","Win Rate","Total Trades","Total Win","Total Loss","Total Fee Paid","Final Balance"]

from fpdf import FPDF

title = 'Optimization Report'


class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        self.set_draw_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(0, 0, 0)
        self.set_line_width(0.1)
        self.cell(w, 9, title, 1, 1, 'C', True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        self.set_font('Helvetica', '', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 6, 'Candidate %d : %s' % (num, label), 0, 1, 'L', True)
        self.ln(4)

    def chapter_body(self, settings:str, txt:list, barplots:List[str]):
        self.set_font('Helvetica', '', 11)
        self.cell(0, 5, f"Settings: {settings}")
        self.ln()
        for line in txt:
            self.cell(self.w, 5, line,align="C")
            self.ln()
        self.set_font('', 'I')
        self.add_images(barplots)

    def add_images(self, barplots:List[str]):
        x_start = 5
        y_start = self.get_y()
        image_width = 94  # Adjust the width to fit the images in a 2x3 grid
        image_height = 63
        for i, barplot in enumerate(barplots):
            if i > 0 and i % 2 == 0:
                y_start += image_height + 5  # Move to the next row after 3 images
                x_start = 5  # Reset x position
            self.image(barplot, x=x_start, y=y_start, w=image_width, h=image_height)
            x_start += image_width + 5  # Move to the next image spot
        self.ln(image_height * 2)  # Add a new line after the images

    def print_record(self, num, title, settings, content, barplots):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(settings, content, barplots)



def sort_csv(path,by):
    # Open the CSV file and read its contents into a list of dictionaries
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    # Sort the data by the "Performance" column in descending order
    data.sort(key=lambda row: float(row[by]), reverse=True)

    base,filename = path.split("/")
    # Write the sorted data back to the CSV file
    with open(f"{base}/sorted_{filename}", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(data)

    return f"{base}/sorted_{filename}"

def filter_by(list:pd.DataFrame, criterion:dict) -> pd.DataFrame:
    """
    Filter the list of algorithms by the given criterion
    """
    df = pd.DataFrame(list)
    df = df[df["kwargs"].str.contains("'stop_loss': None") == False]
    for key,value in criterion.items():
        df = df[df[key] >= value]

    # Total win - (total loss + total commission) > 0
    df = df[df["Total Win"] - (df["Total Loss"] + df["Total Fee Paid"]) > 0]

    # kwargs does not contain string "'stop_loss': None"

    return df
    

def shortlist(path:str) -> pd.DataFrame:
    """
    Return a list of the top N performing algorithms
    after filtering by the given criterion
    """
    df = pd.read_csv(path)
    df = filter_by(df,CRITERION)
    df = df.head(TOP_N)
    return df

def retrieve_bar_chart(path:str) -> str:
    return path


def generate_pdf(shortlisted:pd.DataFrame) -> None:
    # Create a new PDF document
    time_frames = ["week","month","year"]
    types = ["pnl", "profit_factor"]
    pdf = PDF()
    pdf.set_title(title)
    for i in tqdm(range(len(shortlisted)),desc="Generating PDF"):
        record = shortlisted.iloc[i]
        path = os.path.join(os.path.dirname(record["full_path"]),"bar_plots")
        barplots = []
        for time_frame in time_frames:
            for type in types:
                barpath = os.path.join(path,f"{type}_date_{time_frame}.png")
                barplots.append(retrieve_bar_chart(barpath))
        record_title = f"{record['name']} - {record['Pair']} - {record['Performance']}"
        settings = record["kwargs"]
        content = record[COLS].to_string().split("\n")

        pdf.print_record(i, record_title, settings, content, barplots)
    cdate = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if not os.path.exists("pdf"):
        os.mkdir("pdf")
    pdf.output(f'pdf/optimization_report_{cdate}.pdf', 'F')
    return f'pdf/optimization_report_{cdate}.pdf'
        

        


if __name__ == "__main__":
    path = export_csv.main()
    sorted_path = sort_csv(path,BY)
    shortlisted = shortlist(sorted_path)
    pdf_path = generate_pdf(shortlisted)
    strategy_names = shortlisted["name"].unique().tolist() 
    symbols = shortlisted["Pair"].unique().tolist()
    slackbot = SlackOptimizationReportBot(strategy_names=strategy_names, symbols=symbols, pdf_path=pdf_path, csv_path=sorted_path)
    slackbot.send_optimization_report()

    
