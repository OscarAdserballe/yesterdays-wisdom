test_files = [
    "Financial Accounting(16).jpg",
    "14.750x 1(14).jpg",
    "IPE(6).jpg",
    "14.740x 1(15).jpg",
    "Berlin(1).jpg",
    "Introduction to mathematical thinking(10).jpg",
    "International Economics 2(9).jpg",
    "Business strategy and SDGs(1).jpg",
    "Case Studies and Theory Development(11).jpg",
]

import os
dir = "transcription_files"

for file_name in test_files:
    basename = os.path.splitext(file_name)[0].replace(" ", "_").replace('(', '').replace(')', '')
    md_file_path = os.path.join(dir, f"{basename}.md")
    with open(md_file_path, "w+") as f:
        f.write("")
print("Done")