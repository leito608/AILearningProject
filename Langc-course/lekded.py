import csv
import os

from dotenv import load_dotenv

load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lotto_history.csv")

with open(HISTORY_FILE, encoding="utf-8-sig", newline="") as f:
    history_rows = list(csv.DictReader(f))

history_text = "\n".join(
    f"{row['งวดวันที่']} | {row['วันในสัปดาห์']} | {row['เลข 2 ตัวที่ออกรางวัล']}"
    for row in history_rows
)

chat_model = init_chat_model(
    model="gemini-3.5-flash",
    model_provider="google_genai",
    max_retries=3,
    streaming=True,
    temperature=0,
)

system_msg = SystemMessage(content="Use only the local history data provided in the message from oldest to before draw date, do not search online, "
                                   "if not found some of them then return not found data, "
                                   "show result step by step and the final Top 5 in table with score"
                                   "last output example: topic: งวด 1 พฤศจิกายน 2569"
                                    "อันดับ|ตัวเลข|คะแนนรวม|รายละเอียดที่มาของคะแนน"
                                    "1|40|300|ตรงงวด 1 พ.ย. (100) + สถิติวันอาทิตย์ 2 ครั้ง (200)"
                                    "1|62|300|ถัดจากเลขล่าสุด 48 (100) + สถิติวันอาทิตย์ 2 ครั้ง (200)"
                                    "3|87|200|ตรงงวด 1 พ.ย. (100) + สถิติวันอาทิตย์ 1 ครั้ง (100)"
                                    "3|32|200|ตรงงวด 1 พ.ย. (100) + สถิติวันอาทิตย์ 1 ครั้ง (100)"
                                    "3|79|200|ตรงงวด 1 พ.ย. (100) + สถิติวันอาทิตย์ 1 ครั้ง (100)")

prompt = ChatPromptTemplate.from_messages([
    system_msg,
    ("human", """คำสั่ง: ให้ทำหน้าที่เป็นโปรแกรมคำนวณสถิติและให้คะแนนตัวเลขสลากกินแบ่งรัฐบาล (รางวัลเลขท้าย 2 ตัว) ตามเกณฑ์ที่กำหนดอย่างเคร่งครัด โดยหาข้อมูลจริงจากออนไลน์
    เงื่อนไขการให้คะแนน
    ให้ตรวจประวัติผลการออกรางวัลเลขท้าย 2 ตัว ย้อนหลัง 20 ปี จนถึงเวลาปัจจุบัน (พ.ศ. 2550 - 2569) แล้วรวมคะแนนดังนี้:
    1. กฎข้อที่ 1: ตรวจสอบงวดในอดีต (2550-2569) ที่มีผลรางวัลเลขท้าย 2 ตัว ออกตรงกับงวดล่าสุด (คือออก [ระบุเลขงวดล่าสุด เช่น 85]) ให้มอบ 100 คะแนน แก่เลขท้าย 2 ตัวที่ออกใน งวดถัดไป ของปีนั้นๆ
    2. กฎข้อที่ 2: มอบ 100 คะแนน ให้กับเลขท้าย 2 ตัวที่เคยออกในงวดประเพณีเดียวกัน (คือ งวดวันที่ [ระบุวันที่ของงวดที่จะออก เช่น 16 พฤศจิกายน]) ของปี 2550 ถึง 2569
    3. กฎข้อที่ 3: มอบ 100 คะแนน ให้กับเลขท้าย 2 ตัวที่เคยออกในงวดที่ตรงกับวันในสัปดาห์เดียวกัน (งวดที่จะถึงนี้ตรงกับ [ระบุวัน เช่น วันจันทร์]) ย้อนหลัง 10 ปี
    [ข้อบังคับในการแสดงผล]
    1. ห้ามสุ่มเลข เดาเลข หรือสร้างข้อมูลขึ้นมาเองโดยเด็ดขาด ให้ใช้เฉพาะฐานข้อมูลที่อ้างอิงได้จริง
    2. แสดงรายละเอียดการคำนวณแยกตามกฎข้อ 1, ข้อ 2 และข้อ 3 ให้เห็นชัดเจน
    3. จัดลำดับคะแนนรวมทั้งหมด และสรุป Top 10 พร้อมรายละเอียดที่มาของคะแนนในรูปแบบตาราง
    ข้อมูลเป้าหมายที่ต้องการคำนวณ:
    - งวดที่จะคำนวณทำนาย: งวดวันที่ {target_date}

    ข้อมูลประวัติผลรางวัล (ใช้เป็นแหล่งข้อมูลเดียว รูปแบบ: งวดวันที่ | วันในสัปดาห์ | เลข 2 ตัว เรียงจากใหม่ไปเก่า):
    {history}
    """),
])

output_parser = StrOutputParser()   

chain = prompt | chat_model | output_parser

result = chain.invoke({
    "target_date": "16 ตุลาคม 2569",
    "history": history_text,
})

print(result)