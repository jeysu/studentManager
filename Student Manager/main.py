"""Import required modules."""
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5 import uic

class Communicate(QObject):
    """Communicate with signal to update dataframe"""
    updateDataframe = pyqtSignal(pd.DataFrame)

class mainWindow(QMainWindow):
    """Main window"""

    #Initializes dataframes from csv files
    dataframe = pd.read_csv("students.csv")
    course_dataframe = pd.read_csv("courses.csv")

    def __init__(self):
        #Load Main Window UI
        super(mainWindow, self).__init__()
        uic.loadUi("mainWindow.ui", self)
        self.show()

        #Trigger event for buttons in main window
        self.addButton.clicked.connect(self.addClicked)
        self.deleteButton.clicked.connect(self.deleteClicked)
        self.editButton.clicked.connect(self.editClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        self.courseViewButton.clicked.connect(self.courseViewClicked)

        #Store future references to child windows
        self.courseWindow = None
        self.addWindow = None
        self.deleteWindow = None
        self.updateWindow = None

        #Create an object to communicate
        self.communicate = Communicate()
        #Update text browser
        self.read()

    def courseViewClicked(self):
        #Open course window
        self.courseWindow = courseWindow(self.course_dataframe)
        #Update dataframe
        self.courseWindow.communicate.updateDataframe.connect(self.updateCourseDataframeSlot)

    def read(self):
        #Output dataframe as html to text browser
        for index, row in self.dataframe.iterrows():
            course = row["course"]
            # Check if course exists in course dataframe
            if course not in self.course_dataframe["course_code"].tolist():
                # If not found, set course value to "No Course" and enroll status to "No"
                self.dataframe.loc[index, "course"] = "No Course"
                self.dataframe.loc[index, "status"] = "No"
        html_text = self.dataframe.to_html()
        self.outputText.clear()
        self.outputText.setHtml(html_text)

    def addClicked(self):
        #Opens add window
        self.addWindow = addWindow(self.dataframe, self.course_dataframe)
        #Updates dataframe
        self.addWindow.communicate.updateDataframe.connect(self.updateDataframeSlot)

    def deleteClicked(self):
        #Opens delete window
        self.deleteWindow = deleteWindow(self.dataframe)
        #Updates dataframe
        self.deleteWindow.communicate.updateDataframe.connect(self.updateDataframeSlot)

    def editClicked(self):
        #Opens edit window
        self.editWindow = editWindow(self.dataframe, self.course_dataframe)
        #Updates dataframe
        self.editWindow.communicate.updateDataframe.connect(self.updateDataframeSlot)

    def saveClicked(self):
        #Save current dataframe to csv
        self.dataframe.to_csv("students.csv", index=False)

    def updateDataframeSlot(self, new_dataframe):
        #Update dataframe through signal and slot
        self.dataframe = new_dataframe
        self.read()

    def updateCourseDataframeSlot(self, new_course_dataframe):
        #Update course dataframe through signal and slot
        self.course_dataframe = new_course_dataframe
        self.read()

class addWindow(QMainWindow):
    """Add Student Window"""

    def __init__(self, dataframe, course_dataframe):
        #Load Add Window UI
        super(addWindow, self).__init__()
        uic.loadUi("addWindow.ui", self)
        #Adds the course codes from the course dataframe to the drop down combo box
        for index, row in course_dataframe.iterrows():
            value = row['course_code']
            self.courseInput.addItem(value)
        self.show()

        #Button trigger event for add window
        self.submitButton.clicked.connect(self.submitClicked)

        #Store dataframes to local class
        self.dataframe = dataframe
        self.course_dataframe = course_dataframe
        #Communicate object
        self.communicate = Communicate()

    def submitClicked(self):
        # Logic to check for duplicate ID number
        id_number = self.idNumberInput.text()
        existing_student = self.dataframe[self.dataframe["id_number"] == id_number]

        if not existing_student.empty:
            # Display error message if duplicate ID number
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("Duplicate ID Number: " + id_number)
            message.exec()
        else:
            # Logic to add new student to dataframe
            name = self.nameInput.text()
            course = self.courseInput.currentText()
            year = self.yearInput.currentText()
            sex = self.sexInput.currentText()
            if course == "No Course":
                status = "No"
            else:
                status = "Yes"
            student_data = [name, id_number, course, year, sex, status]
            column_names = ["name", "id_number", "course", "year", "sex", "status"]
            new_row = pd.DataFrame(columns=column_names)
            new_row.loc[0] = student_data
            self.dataframe = pd.concat([self.dataframe, new_row], ignore_index=True)

            # Emit signal
            self.communicate.updateDataframe.emit(self.dataframe)
            # Close window
            self.close()

class deleteWindow(QMainWindow):
    """Delete Student Window"""

    def __init__(self, dataframe):
        #Initialize Student Window UI
        super(deleteWindow, self).__init__()
        uic.loadUi("deleteWindow.ui", self)
        self.show()

        #Button trigger event for delete window
        self.submitButton.clicked.connect(self.submitClicked)

        #Store dataframe to local class
        self.dataframe = dataframe
        #Communication object
        self.communicate = Communicate()

    def submitClicked(self):
        # Logic to delete chosen student from dataframe
        student_to_delete = self.deleteInput.text()

        # Confirmation dialog for deleting a student
        reply = QMessageBox.question(self, 'Confirmation', f"Are you sure you want to delete {student_to_delete}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Proceed with deletion if yes
            self.dataframe = self.dataframe.drop(self.dataframe[self.dataframe["id_number"] == student_to_delete].index)
            self.dataframe = self.dataframe.reset_index(drop=True)
            # Emit signal and close window
            self.communicate.updateDataframe.emit(self.dataframe)
            self.close()
        else:
            # Cancel deletion if not confirmed
            return

class editWindow(QMainWindow):
    """Edit Student Window"""

    def __init__(self, dataframe, course_dataframe):
        #Initialize Student Window UI
        super(editWindow, self).__init__()
        uic.loadUi("editWindow.ui", self)
        # Adds the course codes from the course dataframe to the drop down combo box
        for index, row in course_dataframe.iterrows():
            value = row['course_code']
            self.courseInput.addItem(value)
        self.show()

        #Button trigger event for edit window
        self.submitButton.clicked.connect(self.submitClicked)
        self.editSubmitButton.clicked.connect(self.editSubmitClicked)

        #Store dataframe to local class
        self.dataframe = dataframe
        self.course_dataframe = course_dataframe
        #Communicate object
        self.communicate = Communicate()
        #Initialize row index for function use
        self.row_index = None

    def submitClicked(self):
        # Logic to output current values of a given student
        try:
            #Set disabled submit button to true if student is found
            self.editSubmitButton.setEnabled(True)
            student_to_edit = self.editInput.text()
            self.row_index = self.dataframe[self.dataframe["id_number"] == student_to_edit].index
            self.nameInput.setText(str(self.dataframe.loc[self.row_index, "name"].item()))
            self.idNumberInput.setText(str(self.dataframe.loc[self.row_index, "id_number"].item()))
            self.courseInput.setCurrentText(str(self.dataframe.loc[self.row_index, "course"].item()))
            self.yearInput.setCurrentText(str(self.dataframe.loc[self.row_index, "year"].item()))
            self.sexInput.setCurrentText(str(self.dataframe.loc[self.row_index, "sex"].item()))
            self.enrolledInput.setCurrentText(str(self.dataframe.loc[self.row_index, "status"].item()))
        except:
            #Set submit button to false if student is not found
            self.editSubmitButton.setEnabled(False)
            #Show error
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("Student not found")
            message.exec()

    def editSubmitClicked(self):
        # Logic to check for duplicate ID number
        id_number = self.idNumberInput.text()
        # Exclude the current row from the duplicate check
        modified_dataframe = self.dataframe.drop(self.row_index)
        existing_student = modified_dataframe[modified_dataframe["id_number"] == id_number]

        if not existing_student.empty:
            # Display error message if duplicate ID number is found
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("Duplicate ID Number: " + id_number)
            message.exec()
        else:
            # Logic to edit the values of a given student
            name = self.nameInput.text()
            course = self.courseInput.currentText()
            year = int(self.yearInput.currentText())  # Ensure year is converted to integer
            sex = self.sexInput.currentText()
            if course == "No Course":
                status = "No"
            else:
                status = "Yes"

            # Update dataframe with edited values
            self.dataframe.loc[self.row_index, "name"] = name
            self.dataframe.loc[self.row_index, "id_number"] = id_number
            self.dataframe.loc[self.row_index, "course"] = course
            self.dataframe.loc[self.row_index, "year"] = year
            self.dataframe.loc[self.row_index, "sex"] = sex
            self.dataframe.loc[self.row_index, "status"] = status
            # Emit signal and close window
            self.communicate.updateDataframe.emit(self.dataframe)
            self.close()

class courseWindow(QMainWindow):
    """Course View Window"""
    def __init__(self, course_dataframe):
        #Initialize Course Window UI
        super(courseWindow, self).__init__()
        uic.loadUi("courseWindow.ui", self)
        self.show()

        #Button trigger events
        self.addButton.clicked.connect(self.addClicked)
        self.deleteButton.clicked.connect(self.deleteClicked)
        self.editButton.clicked.connect(self.editClicked)
        self.saveButton.clicked.connect(self.saveClicked)
        self.course_dataframe = course_dataframe

        #Initialize child windows
        self.courseAddWindow = None
        self.courseDeleteWindow = None
        self.courseEditWindow = None
        #Communicate object
        self.communicate = Communicate()
        #Output initial course data
        self.read()

    def read(self):
        #Read course data and output as html to text browser
        html_text = self.course_dataframe.to_html()
        self.outputText.clear()
        self.outputText.setHtml(html_text)

    def addClicked(self):
        #Opens Add Course Window
        self.courseAddWindow = courseAddWindow(self.course_dataframe)
        #Update course dataframe
        self.courseAddWindow.communicate.updateDataframe.connect(self.updateCourseDataframeSlot)

    def deleteClicked(self):
        #Opens Delete Course Window
        self.courseDeleteWindow = courseDeleteWindow(self.course_dataframe)
        #Update course dataframe
        self.courseDeleteWindow.communicate.updateDataframe.connect(self.updateCourseDataframeSlot)

    def editClicked(self):
        #Opens Edit Course Window
        self.courseEditWindow = courseEditWindow(self.course_dataframe)
        #Update course dataframe
        self.courseEditWindow.communicate.updateDataframe.connect(self.updateCourseDataframeSlot)

    def saveClicked(self):
        #Save course dataframe to csv
        self.course_dataframe.to_csv("courses.csv", index=False)

    def updateCourseDataframeSlot(self, new_course_dataframe):
        # Update dataframe
        self.course_dataframe = new_course_dataframe
        #Updates text browser with new course dataframe
        self.read()
        #Emit signal to update course dataframe in Main Window
        self.communicate.updateDataframe.emit(self.course_dataframe)

class courseAddWindow(QMainWindow):
    """Add Course Window"""
    def __init__(self, course_dataframe):
        #Initialize Add Course Window UI
        super(courseAddWindow, self).__init__()
        uic.loadUi("courseAddWindow.ui", self)
        self.show()

        #Store dataframe to local class
        self.course_dataframe = course_dataframe
        #Button trigger event
        self.submitButton.clicked.connect(self.submitClicked)
        #Communicate object
        self.communicate = Communicate()

    def submitClicked(self):
        #Logic to add new course to course datafrmae
        course_code = self.courseCodeInput.text()
        course_description = self.courseDescriptInput.text()
        course_data = [course_code, course_description]
        column_names = ["course_code", "course_description"]
        new_row = pd.DataFrame(columns=column_names)
        new_row.loc[0] = course_data
        self.course_dataframe = pd.concat([self.course_dataframe, new_row], ignore_index=True)

        #Emit signal and close window
        self.communicate.updateDataframe.emit(self.course_dataframe)
        self.close()

class courseDeleteWindow(QMainWindow):
    """Delete Course Window"""
    def __init__(self, course_dataframe):
        #Initialize Delete Course Window
        super(courseDeleteWindow, self).__init__()
        uic.loadUi("courseDeleteWindow.ui", self)
        #Adds the course codes from the course dataframe to the drop down combo box
        for index, row in course_dataframe.iterrows():
            value = row['course_code']
            self.courseCodeInput.addItem(value)
        self.show()

        #Store course dataframe to local
        self.course_dataframe = course_dataframe
        #Button trigger event
        self.submitButton.clicked.connect(self.submitClicked)
        #Communicate object
        self.communicate = Communicate()

    def submitClicked(self):
        #Logic to delete a given course
        course_to_delete = self.courseCodeInput.currentText()
        # Confirmation dialog for deleting a course
        reply = QMessageBox.question(self, 'Confirmation', f"Are you sure you want to delete {course_to_delete}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Proceed with deletion if yes
            self.course_dataframe = self.course_dataframe.drop(self.course_dataframe[self.course_dataframe["course_code"] == course_to_delete].index)
            self.course_dataframe = self.course_dataframe.reset_index(drop=True)
            # Emit signal and close window
            self.communicate.updateDataframe.emit(self.course_dataframe)
            self.close()
        else:
            # Cancel deletion if no
            return

class courseEditWindow(QMainWindow):
    """Edit Course Window"""

    def __init__(self, course_dataframe):
        #Initialize Edit Course Window UI
        super(courseEditWindow, self).__init__()
        uic.loadUi("courseEditWindow.ui", self)
        self.show()

        #Button trigger event
        self.submitButton.clicked.connect(self.submitClicked)
        self.editButton.clicked.connect(self.editClicked)

        #Store course dataframe to local
        self.course_dataframe = course_dataframe
        #Communicate object
        self.communicate = Communicate()
        #Initialize row index
        self.row_index = None

    def submitClicked(self):
        #Logic to edit course row
        try:
            #Set edit button to true if course is found
            self.editButton.setEnabled(True)
            course_to_edit = self.editCourseInput.text()
            self.row_index = self.course_dataframe[self.course_dataframe["course_code"] == course_to_edit].index
            self.courseCodeInput.setText(str(self.course_dataframe.loc[self.row_index, "course_code"].item()))
            self.courseDescriptInput.setText(str(self.course_dataframe.loc[self.row_index, "course_description"].item()))
        except:
            #Set edit button to false if course is not found
            self.editButton.setEnabled(False)
            #Show error
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("Course not found")
            message.exec()

    def editClicked(self):
        #Logic to edit given course
        course_code = self.courseCodeInput.text()
        course_description = self.courseDescriptInput.text()
        self.course_dataframe.loc[self.row_index, "course_code"] = course_code
        self.course_dataframe.loc[self.row_index, "course_description"] = course_description
        #Emit signal and close window
        self.communicate.updateDataframe.emit(self.course_dataframe)
        self.close()

def main():
    #Run application event loop
    app = QApplication([])
    window = mainWindow()
    app.exec_()

if __name__ == "__main__":
    main()
