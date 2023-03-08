import streamlit as st
import time
import pandas as pd
from random import sample
import time
from datetime import datetime
from data_reader import Data
import asyncio
import SendEmailFunctions
import streamlit.components.v1 as components
import hydralit_components as hc

data = Data() 

############################################
######### Configuration of the QCM #########
############################################
nb_questions_per_category = 2       ########
timer_in_seconds = 1800             ######## 30 minutes
nb_category = 4                     ########
email_receiver = "qcmtest@yopmail.com" ##### Yopmail address created to make the tests
#email_receiver = "vsuillaud@wewyse.com" ### Works as well
email_sender_info_path = "email_info.json"##
############################################

st.set_page_config(page_title="WEWYSE DATA MANAGEMENT TESTING", page_icon="📚")

###########################################
######## Required global variables ########
###########################################

if 'name' not in st.session_state:
	st.session_state.name = None

if 'num_question' not in st.session_state:
	st.session_state.num_question = -1 ###minus 1 because, the first value of the form is always void

if 'out_of_time' not in st.session_state:
	st.session_state.out_of_time = False

if 'questions_dictionnary' not in st.session_state:
	st.session_state.questions_dictionnary = dict()

if 'start_global_time' not in st.session_state:
	st.session_state.start_global_time = None

if 'local_answer' not in st.session_state:
	st.session_state.local_answer = None

if 'timer_should_run' not in st.session_state:
    st.session_state.timer_should_run = False

if 'qcm_has_started' not in st.session_state:
    st.session_state.qcm_has_started = False

if 'qcm_has_ended' not in st.session_state:
    st.session_state.qcm_has_ended = False

if 'category' not in st.session_state:
	st.session_state.category = None

if 'questions_list' not in st.session_state:
    st.session_state.questions_list = None

if 'answers_submited' not in st.session_state:
    st.session_state.answers_submited = []

if 'category_list' in st.session_state:
    st.session_state.category_list =[]

if 'nav_bar_options' in st.session_state:
    st.session_state.nav_bar_options =[]

if 'nav_bar_selected_option' in st.session_state:
    st.session_state.nav_bar_selected_option = None


####################################
######## Required functions ########
####################################

#Get the list of question according to a specific category
def get_DM_Category(questions,category):
    questions = questions[questions["DM Category"] == category]
    return questions

#Get a sample of questions, equally splitted in the categories
def get_sample_question(questions, category, nb_of_questions):
    return sample(list(questions[questions["Theme"]==category].index),nb_of_questions)

#Initialize the Dictionnary of questions and answers
def initialize_question_dictionnary(questions_categories, questions= st.session_state.questions_list, nb_of_questions = nb_questions_per_category) :
    first = True
    #Questions' selection and dictionnary inistialization
    for category in questions_categories :
        question_sample = get_sample_question(questions, category, nb_of_questions=nb_of_questions)
        ###Add quiestion Business Expertise if DM Expert
        if first and st.session_state.category == "DM Expert":
            business_question = sample(list(data.questions[data.questions["Theme"]=='Business Expertise'].index),1)
            for i,question in enumerate(business_question):
                question_key = 'Business Expertise' + "_" + str(0)
                st.session_state.questions_dictionnary[question_key] = {
                    "Category" : 'Business Expertise',
                    "Question" : questions.loc[question,"Question"],
                    "Submitted answer" : ""
                }
            first = False

        for i, question in enumerate(question_sample) :
            question_key = category + "_" + str(i)
            st.session_state.questions_dictionnary[question_key] = {
                "Category" : category,
                "Question" : questions.loc[question,"Question"],
                "Submitted answer" : ""
            }
        
#Start qcm : initialize required global variable
def start_qcm() :
    if st.session_state.name.replace(' ', '') != '' :
        initialize_question_dictionnary(data.categories[st.session_state.category])
        st.session_state.qcm_has_started = True
        st.session_state.timer_should_run = True

        container_question.warning("Wait a few seconds... your QCM is going to start...")

        SendEmailFunctions.send_start_mail(receiver_email=email_receiver, 
            name_applicant=st.session_state.name,
            email_info_file_path=email_sender_info_path)

        st.session_state.start_question_time = datetime.now()
    else :
        st.warning("You must enter your name to access the test")

def save_answer(key):
    answer = st.session_state.local_answer
    st.session_state.questions_dictionnary[key]["Submitted answer"] = answer
    if len(st.session_state.questions_dictionnary[key]["Submitted answer"])>0 and key not in st.session_state.answers_submited:
        st.session_state.answers_submited.append(key)
    #update global data
    st.session_state.local_answer = None

def display_quizz(category):

    key = category + "_" + str(0)
    with st.form(key=f"quizz_{key}",clear_on_submit=False):

        # writing the questions
        st.markdown("### " + category + " QUESTION")
        st.markdown(st.session_state.questions_dictionnary[key]["Question"])

        #write the answer
        st.session_state.local_answer = st.text_area("Enter your answer",height=150, value=st.session_state.questions_dictionnary[key]["Submitted answer" ])

        explanation_place, button_place = st.columns([5, 1])
        explanation_place.markdown('*To submit your answer click on the following button.*')
        with button_place:
            save = st.form_submit_button(label="Save answer", on_click=save_answer(key))

    key = category + "_" + str(1)
    if category != "Business Expertise":
        with st.form(key=f"quizz_{key}",clear_on_submit=False):
            # writing the questions
            st.markdown("### " + category + " QUESTION")
            key = category + "_" + str(1)
            st.markdown(st.session_state.questions_dictionnary[key]["Question"])

            #write the answer
            st.session_state.local_answer = st.text_area("Enter your answer",height=150, value=st.session_state.questions_dictionnary[key]["Submitted answer" ])

            explanation_place, button_place = st.columns([5, 1])
            explanation_place.markdown('*To submit your answer click on the following button.*')
            with button_place:
                save = st.form_submit_button(label="Save answer", on_click=save_answer(key))


#Function displaying the categories
def show_questions_list():
    st.session_state.category_list = list(set([st.session_state.questions_dictionnary[x]["Category"] for x in st.session_state.questions_dictionnary.keys()]))
    #options of nav_bar
    st.session_state.nav_bar_options = [{'label':x} for x in st.session_state.category_list]
    # override the theme, else it will use the Streamlit applied theme
    over_theme = {'txc_inactive': 'white','menu_background':'grey scale','txc_active':'black','option_active':'grey'}
    font_fmt = {'font-class':'h2','font-size':'150%'}

    # display a horizontal version of the option bar
    st.session_state.nav_bar_selected_option = hc.option_bar(option_definition=st.session_state.nav_bar_options,title='Category',key='PrimaryOption',override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=False)

 
    
#Save the answer, if not out of time, in a global variable
def submit_answer() :
    answer = st.session_state.local_answer

    current_key = question_keys[st.session_state.num_question]
    st.session_state.questions_dictionnary[current_key]["Submitted answer"] = answer

    #update global data
    st.session_state.local_answer = None

#End the QCM : submit last answer and update global data
def end_qcm():
    st.session_state.qcm_has_ended = True

def send_answers():
    st.session_state.qcm_has_ended = True
    submit_answer() #submit the last answer
    SendEmailFunctions.send_results_by_mail(receiver_email=email_receiver, 
    name_applicant=st.session_state.name, 
    dictionary_to_send=st.session_state.questions_dictionnary, 
    email_info_file_path=email_sender_info_path)

#Asynchronous function to display a timer while allowing the user to interact with the page
async def watch(timer_container, start, timer, condition_timer_to_run):
    while condition_timer_to_run:
        remaining_time = timer - int((datetime.now() - start).total_seconds())
        minute = "{:02d}".format(remaining_time // 60)
        seconde = "{:02d}".format(remaining_time % 60)

        timer_container.markdown(
            f"""
            <p class="time">
                Remaining time : {minute} : {seconde}
            </p>
            """, unsafe_allow_html=True)
        #if no time left : update the global data managing the timer and out of time answers 
        if remaining_time < 0 : 
            condition_timer_to_run = False
            st.session_state.out_of_time = True
            timer_container.error("Out of time: Your answers are submitted.")
            st.session_state.qcm_has_ended = True
        await asyncio.sleep(0.1) #/!\ if the candidate answer in less than 0.1s the answer submitted may not be the right one 

################################
######## Initialisation ########
################################

##### Introduction page #####

st.markdown("# DATA MANAGEMENT EC2 TECHNICAL TEST")
container_introduction = st.empty()
container_question = st.empty()

with container_introduction.container() :


    st.write(' ')
    with st.expander("❗️ Information", expanded = True):
        st.write("""
                - You're being evaluated as a part of WeWyse data management recruitment process
                - If you have a question, please contact Anne-Eole Meret-Conti or Benjamin Simonneau
                """)
    st.write(' ')

    #Presentation of the test
    st.markdown(data.info_generale)
        
    #chosing of the category
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)

    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)

    choose=st.radio("Choose your category",("Data PO","DM Expert"))
    st.session_state.category = choose
    #initiate the question list of the specified category
    st.session_state.questions_list = get_DM_Category(data.questions,st.session_state.category)

    st.session_state.name = st.text_input('Before starting the test, please precise you name :', placeholder='Firt name, Last name')


    #Button to start the test & Initialize questions_dictionnary #####
    start_QCM = st.button(label="Start the QCM", on_click=start_qcm)

#############################
######## Display QCM ########
#############################

##### Questions - DURING THE TEST #####


if st.session_state.qcm_has_started :
    
    container_introduction.empty()

    question_keys = list(st.session_state.questions_dictionnary.keys())
    total_questions = len(question_keys) 

    # Question number and timer on the sidebar 
    with st.sidebar:
        st.sidebar.markdown("# Submitted answers " + str(len(st.session_state.answers_submited)) + "/" + str(total_questions))
        timer_container = st.sidebar.empty() 
        show_questions_list()
        explanation_place, button_place = st.columns([3.5, 1.5])
        explanation_place.markdown('*To submit all your answers and end the test click on the following **"End test"** button. If you are out-of-time, your submitted answer will be send.*')
        with button_place:
            end = st.button(label="End test",on_click=end_qcm) 
    
    # For each question, we print it and the answer selection widget
    with container_question.container() :

        display_quizz(st.session_state.nav_bar_selected_option)

                
##### Questions and answers - AFTER THE TEST #####

    if st.session_state.qcm_has_ended :

        st.session_state.timer_should_run = False
        container_question.empty()
        send_answers()

        st.write("Your answers have been sent! Thank you for your time.")

    asyncio.run(watch(timer_container, st.session_state.start_question_time, timer_in_seconds, st.session_state.timer_should_run))



    






