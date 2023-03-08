import pandas as pd

#from google.cloud import 
#import os

#credentials_path="service_account.json"
#os.environ['GOOGLE_APPLICATION_CREDENTIALS']=credentials_path
###access data via API

class Data:
    data=None #donnée de google sheet
    categories=dict()
    questions=None
    info_generale= None
    info_DM_Expert = None
    info_Data_PO = None

    def __init__(self):
        self.data = pd.read_csv("DM_EC2 Test - Questions.csv", sep=",")
        self.questions = self.data[5:].rename(columns=self.data.iloc[4])
        self.info_generale = self.data.iloc[0][3]
        self.info_DM_Expert = self.data.iloc[1][3]
        self.info_Data_PO = self.data.iloc[2][3]
        self.add_categories()

    def add_categories(self):
        for row in range(len(self.questions)):
            if self.questions.iloc[row][0] not in self.categories.keys():
                self.categories[self.questions.iloc[row][0]] = set()
            self.categories[self.questions.iloc[row][0]].add(self.questions.iloc[row][1]) 
        
        self.categories["DM Expert"].discard('Business Expertise')

    def get_list_theme(self,category):
        result = []
        res_dict = dict()
        for row in range(len(self.questions)):
            for theme in self.categories[category]:
                if theme not in res_dict.keys():
                    res_dict[theme] = list()
                res_dict[theme].append(self.questions.iloc[row][3])

        return res_dict

    def extract_Business_Expertise_question(self):
        for row in range(len(self.questions)):
            if self.questions.iloc[row][0] == "DM Expert" and self.questions.iloc[row][1] == 'Business Expertise':
                return [row]
