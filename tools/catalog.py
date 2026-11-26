"""Everything the site lists: sections, subjects and files.

Sources stay where Harsh keeps them; tools/prepare.py makes the public copies.
Pages are 1-based. A paper set from a combined PDF lists its pages in ISE 1, ISE 2, ESE order.
"""

PYQ = r"C:\Users\admin\Documents\IT Batch 2027 pyqs"
QBN = r"C:\Users\admin\Documents\Question Bank & Notes"
COMBINED_5 = QBN + r"\5th Sem PYQ.pdf"
COMBINED_6 = QBN + r"\6th Sem PYQ.pdf"
COMBINED_7 = QBN + r"\7th Sem PYQ.pdf"
FIRST_YEAR = QBN + r"\First Year Question Paper 2022 - 23.pdf"

# Sections in site order. key is what SUBJECTS use as "sem"; css picks the section colour.
SECTIONS = [
    dict(key=1, title="Semester I", short="Sem I", slug="sem-1", css="s1", note="First year, common to all branches (CBCGS-HME 2020)"),
    dict(key=2, title="Semester II", short="Sem II", slug="sem-2", css="s2", note="First year, common to all branches (CBCGS-HME 2020)"),
    dict(key=3, title="Semester III", short="Sem III", slug="sem-3", css="s3", note=""),
    dict(key=4, title="Semester IV", short="Sem IV", slug="sem-4", css="s4", note=""),
    dict(key=5, title="Semester V", short="Sem V", slug="sem-5", css="s5", note=""),
    dict(key=6, title="Semester VI", short="Sem VI", slug="sem-6", css="s6", note=""),
    dict(key=7, title="Semester VII", short="Sem VII", slug="sem-7", css="s7", note=""),
    dict(key="ob", title="Other branches", short="Other branches", slug="other-branches", css="sob",
         note="Not IT. Papers from other branches that overlap IT subjects"),
]
SECTION = {s["key"]: s for s in SECTIONS}

# group: core (IT subject this batch took), elective (another option in the same slot),
# other (older syllabus, kept because the questions still help)
SUBJECTS = [
    # Semester I (first year)
    dict(sem=1, slug="mathematics-i", name="Mathematics I", code="", group="core", aka="Maths 1 M1 FE"),
    dict(sem=1, slug="physics", name="Physics", code="", group="core", aka="Engineering Physics FE"),
    dict(sem=1, slug="basic-electrical-engineering", name="Basic Electrical Engineering", code="", group="core", aka="BEE Electrical FE"),
    dict(sem=1, slug="engineering-graphics", name="Engineering Graphics and Design", code="", group="core", aka="EG EGD Drawing FE"),
    dict(sem=1, slug="workshop-practice-i", name="Workshop and Manufacturing Practice I", code="", group="core", aka="Workshop WMP FE"),
    # Semester II (first year)
    dict(sem=2, slug="mathematics-ii", name="Mathematics II", code="", group="core", aka="Maths 2 M2 FE"),
    dict(sem=2, slug="chemistry", name="Chemistry", code="", group="core", aka="Engineering Chemistry FE"),
    dict(sem=2, slug="programming-problem-solving", name="Programming for Problem Solving", code="", group="core", aka="PPS C programming FE"),
    dict(sem=2, slug="english-professional-communication", name="English for Professional Communication", code="", group="core", aka="EPC English FE"),
    dict(sem=2, slug="engineering-mechanics", name="Engineering Mechanics", code="", group="core", aka="EM Mechanics FE"),
    # Semester III
    dict(sem=3, slug="uhv-ii", name="Universal Human Values II", code="HSMC-301", group="core", aka="UHV UHV-II UHV 2"),
    dict(sem=3, slug="maths-iii", name="Mathematics III", code="BSC-IT-301", group="core", aka="Maths 3 M3 Engineering Mathematics"),
    dict(sem=3, slug="digital-circuit-design", name="Digital Circuit Design", code="ESC-IT-301", group="core", aka="DCD"),
    dict(sem=3, slug="dsa", name="Data Structures and Algorithms", code="PCC-IT-301", group="core", aka="DSA DS"),
    dict(sem=3, slug="dbms", name="Database Management Systems", code="PCC-IT-302", group="core", aka="DBMS SQL"),
    # Semester IV
    dict(sem=4, slug="maths-iv", name="Mathematics IV", code="BSC-IT-401", group="core", aka="Maths 4 M4 Statistics Probability"),
    dict(sem=4, slug="coa", name="Computer Organization, Architecture and Microprocessors", code="ESC-IT-401", group="core", aka="COA COAM Microprocessor 8086"),
    dict(sem=4, slug="nosql", name="NoSQL", code="PCC-IT-401", group="core", aka="No SQL MongoDB"),
    dict(sem=4, slug="computer-networks", name="Computer Networks", code="PCC-IT-402", group="core", aka="CN Networking"),
    # Semester V
    dict(sem=5, slug="operating-system", name="Operating System", code="PCC-IT-501", group="core", aka="OS"),
    dict(sem=5, slug="automata-theory", name="Automata Theory", code="PCC-IT-502", group="core", aka="AT TOC Theory of Computation"),
    dict(sem=5, slug="web-programming", name="Web Programming", code="PCC-IT-503", group="core", aka="WP Web Dev HTML"),
    dict(sem=5, slug="cns", name="Cryptography and Network Security", code="PCC-IT-504", group="core", aka="CNS Crypto Security"),
    dict(sem=5, slug="soft-skills", name="Soft Skill and Interpersonal Communication", code="HSMC-501", group="core", aka="SSIC Soft Skills"),
    dict(sem=5, slug="full-stack-development-i", name="Full Stack Development I", code="HME-IT PS501", group="elective",
         note="Professional skills (HME) track", aka="FSD Full Stack"),
    # Semester VI
    dict(sem=6, slug="wpmh", name="Work Place Mental Health", code="HSMC-601", group="core", aka="WPMH Mental Health"),
    dict(sem=6, slug="dmbi", name="Data Mining and Business Intelligence", code="PCC-IT-601", group="core", aka="DMBI Data Mining BI"),
    dict(sem=6, slug="software-engineering", name="Software Engineering", code="PCC-IT-602", group="core", aka="SE"),
    dict(sem=6, slug="artificial-intelligence", name="Artificial Intelligence", code="PEC-IT 6013", group="core",
         note="Professional Elective I", aka="AI PE1 PE-I"),
    dict(sem=6, slug="intro-ai-ds", name="Introduction to Artificial Intelligence and Data Science", code="", group="core",
         note="Open Elective I", aka="AIDS AI DS OE1 OE-I"),
    dict(sem=6, slug="analysis-of-algorithms", name="Analysis of Algorithms", code="PEC-IT 6015", group="elective",
         note="Professional Elective I, another option", aka="AOA Algorithms"),
    dict(sem=6, slug="english-competitive-exams", name="English for Competitive Exams", code="OEC-6022", group="elective",
         note="Open Elective I, another option", aka="English OE"),
    # Semester VII
    dict(sem=7, slug="ml-it-app-dev", name="Machine Learning for IT Application Development", code="PCC-IT-701", group="core", aka="ML MLITAD"),
    dict(sem=7, slug="big-data-analytics", name="Big Data Analytics", code="PCC-IT-702", group="core", aka="BDA Hadoop"),
    dict(sem=7, slug="devops", name="DevOps", code="PEC-IT 7013", group="core", note="Professional Elective II", aka="PE2 PE-II Dev Ops"),
    dict(sem=7, slug="web-analytics-ir", name="Web Analytics and Information Retrieval", code="PEC-IT 7023", group="core",
         note="Professional Elective III", aka="WAIR WA IR PE3"),
    dict(sem=7, slug="japanese-i", name="Japanese Language I", code="OEC-70119", group="core", note="Open Elective II", aka="Japanese OE2 OE-II"),
    dict(sem=7, slug="user-interaction-design", name="User Interaction Design", code="PEC-IT 7024", group="other",
         note="Professional Elective IV, older syllabus (2022)", aka="UID UI UX"),
    dict(sem=7, slug="management-information-system", name="Management Information System", code="", group="other",
         note="Open elective, older syllabus (2022)", aka="MIS"),
    dict(sem=7, slug="design-thinking", name="Design Thinking and Problem Solving", code="", group="other",
         note="Open Elective II, older syllabus (2022)", aka="Design Thinking"),
    dict(sem=7, slug="disaster-management", name="Disaster Management and Mitigation Methods", code="", group="other",
         note="Open elective, older syllabus (2022)", aka="Disaster"),
    # Other branches (not IT)
    dict(sem="ob", slug="machine-learning-other-branches", name="Machine Learning, other branches", code="", group="core",
         note="Computer Engineering, AIML and AI and DS papers", aka="ML Machine Learning AIML AIDS Computer"),
]

OWN = ["ISE 1", "ISE 2", "ESE"]


def paper(subject, year, src, exams=OWN, pages=None, note="", own=False, redact=None, label="", tag="", yearlabel=""):
    """label: extra words after the exams (e.g. the branch); tag: makes the id unique when a subject
    has two sets from the same year; yearlabel: shown instead of the year (e.g. 2022-23)."""
    return dict(kind="paper", subject=subject, year=year, src=src, exams=exams, pages=pages, note=note, own=own,
                redact=redact or {}, label=label, tag=tag, yearlabel=yearlabel)


def bank(subject, title, src, note=""):
    return dict(kind="qb", subject=subject, title=title, src=src, note=note)


def notes(subject, title, src, note=""):
    return dict(kind="notes", subject=subject, title=title, src=src, note=note)


# Cover boxes for another student's handwritten name, division and roll number
# (6th Sem PYQ.pdf pages 19 to 23). Fractions of page width and height: x0, y0, x1, y1.
NAME_BOXES = {
    19: [(0.72, 0.095, 0.965, 0.148), (0.810, 0.140, 0.880, 0.171)],
    20: [(0.72, 0.075, 0.960, 0.135), (0.780, 0.115, 0.852, 0.150)],
    21: [(0.78, 0.012, 1.000, 0.080), (0.860, 0.070, 0.955, 0.099)],
    22: [(0.72, 0.068, 1.000, 0.125), (0.835, 0.110, 0.925, 0.145)],
    23: [(0.65, 0.080, 0.910, 0.133), (0.790, 0.120, 0.895, 0.165)],
}
OLD = "Older syllabus (CBCGS-H 2019 / HME 2020)"
FE = dict(src=FIRST_YEAR, year=2023, yearlabel="2022-23")

ITEMS = [
    # ---- Semester I (first year 2022-23; ISE Dec 2022 and Jan 2023, ESE Feb 2023)
    paper("mathematics-i", pages=[25, 24, 32, 33, 41, 42, 43], **FE),
    paper("physics", pages=[29, 34, 39, 40], **FE),
    paper("basic-electrical-engineering", pages=[27, 28, 35, 44, 45, 46], **FE),
    paper("engineering-graphics", pages=[30, 31, 36, 37, 47, 48, 49], **FE),
    paper("workshop-practice-i", pages=[26, 38, 50], **FE),
    # ---- Semester II (first year 2022-23; ISE Apr and May 2023, ESE May/June 2023)
    paper("mathematics-ii", exams=["ISE 1", "ESE"], pages=[11, 18, 19, 20], **FE),
    paper("chemistry", pages=[10, 6, 7, 21, 22, 23], **FE),
    paper("programming-problem-solving", pages=[9, 3, 1, 2], **FE),
    paper("english-professional-communication", pages=[8, 4, 5, 12, 13], **FE),
    paper("engineering-mechanics", exams=["ESE"], pages=[14, 15, 16, 17], **FE),
    # ---- Semester III (Batch 2027, exams in 2024)
    paper("uhv-ii", 2024, PYQ + r"\UHV-II Sem III 2024.pdf", own=True),
    paper("maths-iii", 2024, PYQ + r"\Maths-III Sem-III 2024.pdf", own=True),
    paper("digital-circuit-design", 2024, PYQ + r"\DCD Sem-III 2024.pdf", own=True),
    paper("dsa", 2024, PYQ + r"\DSA Sem-III 2024.pdf", own=True),
    paper("dbms", 2024, PYQ + r"\DBMS Sem -III 2024.pdf", own=True),
    # ---- Semester IV (2025)
    paper("maths-iv", 2025, PYQ + r"\Maths IV Sem IV 2025.pdf", exams=["ISE 2", "ESE"], own=True),
    bank("maths-iv", "All modules", QBN + r"\Maths SE question bank.xlsx"),
    paper("coa", 2025, PYQ + r"\COA. & Micropro. Sem IV 2025.pdf", own=True),
    paper("nosql", 2025, PYQ + r"\NoSQL Sem IV 2025.pdf", own=True),
    paper("computer-networks", 2025, PYQ + r"\Computer Networks Sem IV 2025.pdf", own=True),
    bank("computer-networks", "Modules 4 to 6, with PYQ tags", QBN + r"\CN mod 4,5,6 question bank.xlsx"),
    bank("computer-networks", "Modules 4 to 6", QBN + r"\Computer Networks Question Bank*.docx"),
    # ---- Semester V (2025, plus the 2024 set)
    paper("operating-system", 2025, PYQ + r"\Operating Sys. Sem V 2025.pdf", own=True),
    paper("operating-system", 2024, COMBINED_5, pages=[18, 17, 19, 20]),
    bank("operating-system", "Modules 1 to 3", QBN + r"\Operating System Mod 1 to 3.xlsx"),
    paper("automata-theory", 2025, PYQ + r"\Automata Theory Sem V 2025.pdf", own=True),
    paper("automata-theory", 2024, COMBINED_5, exams=["ISE 1", "ISE 2", "ISE 3", "ESE"], pages=[4, 5, 6, 7, 8]),
    bank("automata-theory", "Modules 1 to 6", QBN + r"\Automata Theory or TOC Mod 1 to 6.xlsx"),
    paper("web-programming", 2024, COMBINED_5, pages=[14, 13, 15, 16]),
    bank("web-programming", "Modules 1 to 6", QBN + r"\Web Programming Mod 1 to 6.pdf", note="The college question bank"),
    bank("web-programming", "Modules 1 to 6, formatted", QBN + r"\Web Programming mod 1-6 Formatted.xlsx"),
    bank("web-programming", "Modules 1 to 3, with PYQ marks", QBN + r"\Web Programming Mod 1-3.xlsx"),
    paper("cns", 2025, PYQ + r"\C.&N.Security. SemV 2025.pdf", own=True),
    paper("cns", 2024, COMBINED_5, pages=[10, 9, 11, 12]),
    bank("cns", "Modules 1 to 3", QBN + r"\Cryptography&NetworkSecurity mod 1-3.xlsx"),
    bank("cns", "Modules 4 to 6", QBN + r"\Cryptography&NetworkSecurity Mod 4-6.xlsx"),
    paper("soft-skills", 2025, PYQ + r"\SoftSkills & IC Sem V 2025.pdf", own=True),
    paper("soft-skills", 2024, COMBINED_5, pages=[21, 22, 23, 24, 25]),
    bank("soft-skills", "Modules 1 to 6", QBN + r"\Soft Skills Mod 1 to 6.pdf"),
    paper("full-stack-development-i", 2024, COMBINED_5, exams=["ESE"], pages=[3]),
    # ---- Semester VI (2026, plus the 2025 set)
    paper("wpmh", 2026, PYQ + r"\WPMH Sem VI 2026.pdf", own=True),
    paper("wpmh", 2025, COMBINED_6, pages=[22, 18, 3], redact={22: NAME_BOXES[22]}),
    bank("wpmh", "Modules 1 to 6", QBN + r"\WorkPlaceMentalHealth Mod 1 to 6.pdf"),
    paper("dmbi", 2026, PYQ + r"\DMBI Sem-VI 2026.pdf", own=True),
    paper("dmbi", 2025, COMBINED_6, pages=[23, 24, 14, 4, 5, 6], redact={23: NAME_BOXES[23]}),
    paper("software-engineering", 2026, PYQ + r"\SoftwareEngg. Sem-VI 2026.pdf", own=True),
    paper("software-engineering", 2025, COMBINED_6, pages=[21, 17, 9, 10], redact={21: NAME_BOXES[21]}),
    bank("software-engineering", "Modules 1 to 3", QBN + r"\SoftwareEngineering Mod 1 to 3.xlsx"),
    notes("software-engineering", "The syllabus explained in simple words", QBN + r"\Notes\SE Syllabus Explanation.pdf"),
    paper("artificial-intelligence", 2026, PYQ + r"\PE-1(A.I.) Sem VI 2026.pdf", own=True),
    bank("artificial-intelligence", "Modules 1 to 6", QBN + r"\PE AI Mod 1 to 6 .xlsx"),
    bank("artificial-intelligence", "Modules 1 to 3", QBN + r"\AI Mod 1 to 3.xlsx"),
    paper("intro-ai-ds", 2026, PYQ + r"\OE-1 (A.I.& D.S.) Sem VI 2026.pdf", own=True),
    bank("intro-ai-ds", "Modules 1 to 6", QBN + r"\AIDS Mod 1 to 6.docx"),
    paper("analysis-of-algorithms", 2025, COMBINED_6, pages=[20, 13, 11, 12], redact={20: NAME_BOXES[20]}),
    paper("english-competitive-exams", 2025, COMBINED_6, pages=[19, 15, 16, 7, 8], redact={19: NAME_BOXES[19]}),
    # ---- Semester VII (2026, plus 2022 papers from the older syllabus)
    paper("ml-it-app-dev", 2026, PYQ + r"\ML for ITAppDev. Sem VII 2026.pdf", own=True),
    paper("ml-it-app-dev", 2022, COMBINED_7, exams=["ESE"], pages=[10, 11], note=OLD),
    bank("ml-it-app-dev", "Modules 1 to 6", QBN + r"\ML Mod 1 to 6.pdf"),
    notes("ml-it-app-dev", "Exam answer key", QBN + r"\Notes\ML Notes\ML_Exam_Answer_Key.pdf"),
    paper("big-data-analytics", 2026, PYQ + r"\Bigdata analytics Sem VII 2026.pdf", own=True),
    bank("big-data-analytics", "Modules 1 to 6", QBN + r"\BigDataAnalytics Mod 1 to 6.pdf"),
    notes("big-data-analytics", "Exam answer key", QBN + r"\Notes\BigDataAnalytics Notes\BDA_Exam_Answer_Key.pdf"),
    notes("big-data-analytics", "Numericals, solved", QBN + r"\Notes\BigDataAnalytics Notes\BDA Numericals.pdf"),
    paper("devops", 2026, PYQ + r"\PE-2(DevOps) Sem VII 2026.pdf", own=True),
    bank("devops", "Modules 1 to 6", QBN + r"\DevOps Mod 1 to 6.pdf"),
    notes("devops", "Exam answer key", QBN + r"\Notes\DevOps_Exam_Answer_Key.pdf"),
    paper("web-analytics-ir", 2026, PYQ + r"\W.A.& I.R. Sem VII 2026.pdf", own=True),
] + [
    notes("web-analytics-ir", f"Module {n}", QBN + rf"\Notes\WAIR Notes\WAIR Mod {n}.docx") for n in range(1, 7)
] + [
    paper("japanese-i", 2026, PYQ + r"\OE-2(Japanese-1) Sem VII 2026.pdf", own=True),
    bank("japanese-i", "Modules 1 to 3", QBN + r"\Japanese mod 1 to 3.docx"),
    bank("japanese-i", "Modules 3 to 6", QBN + r"\Japanese Mod 3 to 6.docx"),
    paper("user-interaction-design", 2022, COMBINED_7, exams=["ESE"], pages=[8, 9], note=OLD),
    paper("management-information-system", 2022, COMBINED_7, exams=["ESE"], pages=[3], note=OLD),
    paper("design-thinking", 2022, COMBINED_7, exams=["ESE"], pages=[4, 5], note=OLD),
    paper("disaster-management", 2022, COMBINED_7, exams=["ESE"], pages=[6], note=OLD),
    # ---- Other branches: Machine Learning papers from Computer Engineering, AIML and AI and DS
    paper("machine-learning-other-branches", 2024, COMBINED_5, exams=["ESE"], pages=[1, 2], tag="comp",
          label="Computer Engineering (AI and DS specialisation)"),
    paper("machine-learning-other-branches", 2022, COMBINED_7, exams=["ESE"], pages=[1, 2], tag="aiml", note=OLD,
          label="AIML branch, Fundamentals of Machine Learning (CC-AIML 503)"),
    paper("machine-learning-other-branches", 2022, COMBINED_7, exams=["ESE"], pages=[7], tag="aids", note=OLD,
          label="AI and DS branch, Machine Learning (PCC-AIDS503)"),
]

# Left out on purpose (Harsh, 23 Nov 2026): the ML Module 1 to 6 lecture slides are a faculty
# member's own material. The CNS ESE Dec 2024 also sits at 6th Sem PYQ.pdf pages 1-2; the copy
# in the 5th Sem file is used instead.
EXCLUDED_NOTE = "ML lecture slides (faculty material) are not published."


def item_id(it):
    """Stable id used in URLs and file names."""
    if it["kind"] == "paper":
        return f'{it["subject"]}-{it["year"]}-papers' + (f'-{it["tag"]}' if it.get("tag") else "")
    words = "".join(ch if ch.isalnum() else "-" for ch in it["title"].lower())
    while "--" in words:
        words = words.replace("--", "-")
    return f'{it["subject"]}-{"qb" if it["kind"] == "qb" else "notes"}-{words.strip("-")}'
