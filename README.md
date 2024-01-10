# Optical character recognition
### Build APIs for Optical Character Recognition (OCR): Extracting relevant details from identity documents like the customer’s name, Date of birth, address, the unique identification number.  

So before performing OCR we first check if the input image is a valid id proof or not. Classifier trained using Google’s cloud vision services.  

Then for valid id documents we first apply some image enhancement functions, like grayscaling image, increasing sharpness/ contrast/ histogram equalization, reducing blur through OpenCV and Python Imaging Library functions (PIL). After preprocessing we perform the text extraction using Gcloud’s OCR API.   

The extracted text was displayed in a jsonified form in the localhost, and we used python’s Flask api for that.  

We performed Text extraction from salary slips (in the form of pdf/images): using open source libraries like pymupdf, pytesseract, Camelot and compared the accuracies with that of Googles cloud vision. 

Build prediction model for determining the loan status for active users:  the task was to build prediction model to determine the possibility of loan returnability on time for current customers. We had information of past customers like income levels, their age, asset value, net worth, loan amount disbursed, the interest rate, loan type taken and we had labels if they had defaulted, repayed on time (I.e. loan is closed) or if the person is an open defaulter.  

We prepocessed the data by removing outliers, replacing Null values and removing irrelevant features. Categorical data was one-hot encoded and numerical data was normalized for efficient gradient descent. 

We trained an ANN model with softmax activation  (90% validation accuracy) on the output layer and added a dropout layer to prevent overfitting. Achieved better accuracy than ML models like SVM (55% accuracy) or MNB. 

Please refer to this report for detailed insights on the algorithms used, models trained and the kind of data used.

 
