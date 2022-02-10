from download_exam import download_exam
from constants import get_exams, action

# TODO: make separate private/public keyfiles for user vs. alias encryptions

exams = get_exams()

print("\nDownloading and organizing data for the follwing exams:\n", exams)

for exam in exams:

    exam_no = exam.strip()  # strip to remove trailing whitespace

    # Download + organize into /rawdata
    download_exam(exam_no, action)    # uses alias token to get jsession and downloads