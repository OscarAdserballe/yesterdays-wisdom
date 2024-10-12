# get_notes.py
import os
from utils.objects import Class, Note

def create_notes_objects(directory) -> list[Class]:
    classes = []

    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
            
        if os.path.isdir(folder_path):
            class_obj = Class(folder_name)
            
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                
                if os.path.isfile(file_path):
                    note = Note(
                        file_name=file_name,
                        path=file_path,
                        class_name=folder_name
                    )
                    note.class_name = folder_name  # Assign the class name to the note
                    class_obj.add_note(note)
            
            classes.append(class_obj)
            
    return classes
