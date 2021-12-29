from download_exam import download_exam
from setup import get_exams, action
from organize import move2raw

# TODO: make separate private/public keyfiles for user vs. alias encryptions



exams = get_exams()
for exam in exams:
    exam = str(exam.strip())
    print("\nDownloading and organizing data for exam ", exam)
    # Download + organize into /rawdata
    download_exam(exam_no=exam, action=action)    # uses alias token to get jsession and downloads
