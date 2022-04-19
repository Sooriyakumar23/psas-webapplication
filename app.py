# Importing libraries
import streamlit as st
from PIL import Image
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import datetime as dt
from pushbullet import Pushbullet

st.set_page_config(page_title="PSAS-Web-App", page_icon=":computer:", layout="wide")

def WebApp():
	st.title("PSAS-Dashboard")
	menu1 = ['Home', 'Login', 'Signup', 'Change credentials']
	choice1 = st.sidebar.selectbox('Menu', menu1)

	if choice1 == 'Login':
		st.subheader('Login & Dashboard section')

		username = st.sidebar.text_input('User Name')
		password = st.sidebar.text_input('Password', type='password')

		if st.sidebar.checkbox('Login'):
			with open('credentials.txt', 'r') as f:
				cred = f.read().split("\n")
			exist = False

			for elements in cred:
				element = elements.split(",")
				if (element[0] == username) and (element[1] == password):
					uid = element[2]
					exist = True
					break

			if exist == True:
				menu2 = ['Profile', 'Current', 'History']
				choice2 = st.sidebar.selectbox('Details', menu2)

				if choice2 == 'Profile':
					color = st.color_picker('Pick A Color', '#00f900')
					html_username = f'<p style="font-family:Courier; color:{color}; font-size: 50px;">User Name : {element[0]}</p>'
					html_password = f'<p style="font-family:Courier; color:{color}; font-size: 50px;">Password : {element[1]}</p>'
					html_uid = f'<p style="font-family:Courier; color:{color}; font-size: 50px;">Unique ID : {element[2]}</p>'

					st.markdown(html_username, unsafe_allow_html=True)
					st.markdown(html_password, unsafe_allow_html=True)
					st.markdown(html_uid, unsafe_allow_html=True)

				elif choice2 == 'Current':
					st.header('Current')

					current_doc = db.collection('data').document(uid[:5]).get()

					if current_doc.exists:
						data = current_doc.to_dict()

						current_time = data["current"]
						current_date = data["date"]

						latest_time = f'<p style="font-family:Courier; color:yellow; font-size: 50px;">Latest updated time : {current_time} @ {current_date}</p>'
						st.markdown(latest_time, unsafe_allow_html=True)

						st.write(data)

						st.subheader("Posture Assessment")

						pc1 = data["pc1"]
						pc2 = data["pc2"]
						pc3 = data["pc3"]
						pc4 = data["pc4"]
						pc5 = data["pc5"]
						pc6 = data["pc6"]
						pc7 = data["pc7"] #/data["pfullbar"]

						posture_dict = {'Name':["pc1", "pc2", "pc3", "pc4", "pc5", "pc6", "pc7"],
										'Posture Conditions':[pc1, pc2, pc3, pc4, pc5, pc6, pc7]}

						st.bar_chart(pd.DataFrame(posture_dict).set_index('Name'))

						st.subheader("Stress Assessment")

						if data['stress'] == 'stress':
							color = 'RED'
						elif data['stress'] == 'not stress':
							color = 'GREEN'

						stress = f'<p style="font-family:Courier; color:{color}; font-size: 20px;">{data["stress"]}</p>'
						st.markdown(stress, unsafe_allow_html=True)

						ef = data["ef"]
						pe = data["pe"]
						fr = data["fr"]
						md = data["md"]
						td = data["td"]
						phd = data["pd"]
						nasatlx = data["nasatlx"] #/data["sfullbar"]

						stress_dict = {'Name':['Nasa TLX', 'effort', 'performance', 'frustration', 'mental demand', 'physical demand', 'temporal demand'],
										'Stress Factors':[nasatlx, ef, pe, fr, md, phd, td]}

						st.bar_chart(pd.DataFrame(stress_dict).set_index('Name'))

						##### Push Notification #####
						API_key = 'o.xPtYiTp5ZuK0slEHH3fuAFxuoDVrV15c'
						text_stress = f'You are in {data["stress"]}. Your Nasa TLX is {nasatlx}.'
						text_posture = f'Your highest posture condition: {["pc1", "pc2", "pc3", "pc4", "pc5", "pc6", "pc7"][[pc1, pc2, pc3, pc4, pc5, pc6, pc7].index(max([pc1, pc2, pc3, pc4, pc5, pc6, pc7]))]} = {max([pc1, pc2, pc3, pc4, pc5, pc6, pc7])}.'
						pb = Pushbullet(API_key)
						push_posture = pb.push_note('Postural Status', text_posture)
						push_stress = pb.push_note('Occupational Stress Status', text_stress)

					else:
						st.error('No data found under this UID.....')

				elif choice2 == 'History':
					st.header('History')

					d = st.date_input("Select the date to show the history", dt.date(2022, 3, 18))

					st.write(d)

					p = st.radio(
					     "Select period to display history",
					     ('AM', 'PM'))

					if p == 'AM':
					     st.write('You selected AM.')
					elif p == 'PM':
					     st.write("You selected PM.")

					#--------------------------------------------# Inputs #--------------------------------------------#
					date_string = str(d) # '2022-03-17', '2022-03-16', '2022-03-15', '2022-03-14', ......
					period = p # 'PM', 'AM'

					UID = uid #'1TDAwGqWeiNlVCWVSCiYfO6pLAb2'
					#--------------------------------------------------------------------------------------------------#

					docs = db.collection('data').stream()

					#st.write(date_string, period, UID)
					document = []
					for doc in docs:
						try:
						    if doc.to_dict()['uniqueid'] == UID:
						    	if doc.to_dict()['date'][:-5] == date_string:
						    		if doc.to_dict()['time'] == period:
						    			document.append(doc.to_dict())
						except:
							pass

					if len(document) == 0:
						st.error("No documents found under this UID for this date.")

					else:
						document = document[0]
						st.write(document)

						menu3 = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6', 'PC7',
								'Effort', 'Performance', 'Frustration', 'Temporal Demand', 'Mental Demand', 'Physical Demand', 'Nasa TLX']
						choice3 = st.sidebar.selectbox('Factors', menu3)


						if choice3 == 'PC1':
							pc1_bar = []
							for j in range(24):
								pc1_bar.append(document[f"pc1value{j}"])
							pc1_history = {'Values':pc1_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pc1_history).set_index('Duration'))

						elif choice3 == 'PC2':
							pc2_bar = []
							for j in range(24):
								pc2_bar.append(document[f"pc2value{j}"])
							pc2_history = {'Values':pc2_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pc2_history).set_index('Duration'))

						elif choice3 == 'PC3':
							pc3_bar = []
							for j in range(24):
								pc3_bar.append(document[f"pc3value{j}"])
							pc3_history = {'Values':pc3_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pc3_history).set_index('Duration'))

						elif choice3 == 'PC4':
							pc4_bar = []
							for j in range(24):
								pc4_bar.append(document[f"pc4value{j}"])
							pc4_history = {'Values':pc4_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pc4_history).set_index('Duration'))

						elif choice3 == 'PC5':
							pc5_bar = []
							for j in range(24):
								pc5_bar.append(document[f"pc5value{j}"])
							pc5_history = {'Values':pc5_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pc5_history).set_index('Duration'))

						elif choice3 == 'PC6':
							pc6_bar = []
							for j in range(24):
								pc6_bar.append(document[f"pc6value{j}"])
							pc6_history = {'Values':pc6_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pc6_history).set_index('Duration'))

						elif choice3 == 'PC7':
							pc7_bar = []
							for j in range(24):
								pc7_bar.append(document[f"pc7value{j}"])
							pc7_history = {'Values':pc7_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pc7_history).set_index('Duration'))

						elif choice3 == 'Effort':
							ef_bar = []
							for j in range(24):
								ef_bar.append(document[f"efvalue{j}"])
							ef_history = {'Values':ef_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(ef_history).set_index('Duration'))

						elif choice3 == 'Performance':
							pe_bar = []
							for j in range(24):
								pe_bar.append(document[f"pevalue{j}"])
							pe_history = {'Values':pe_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pe_history).set_index('Duration'))

						elif choice3 == 'Frustration':
							fr_bar = []
							for j in range(24):
								fr_bar.append(document[f"frvalue{j}"])
							fr_history = {'Values':fr_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(fr_history).set_index('Duration'))

						elif choice3 == 'Temporal Demand':
							td_bar = []
							for j in range(24):
								td_bar.append(document[f"tdvalue{j}"])
							td_history = {'Values':td_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(td_history).set_index('Duration'))

						elif choice3 == 'Mental Demand':
							md_bar = []
							for j in range(24):
								md_bar.append(document[f"mdvalue{j}"])
							md_history = {'Values':md_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(md_history).set_index('Duration'))

						elif choice3 == 'Physical Demand':
							pd_bar = []
							for j in range(24):
								pd_bar.append(document[f"pdvalue{j}"])
							pd_history = {'Values':pd_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(pd_history).set_index('Duration'))

						elif choice3 == 'Nasa TLX':
							nasatlx_bar = []
							for j in range(24):
								nasatlx_bar.append(document[f"nasatlx{j}"])
							nasatlx_history = {'Values':nasatlx_bar,
											'Duration':['00.00', '00.30', '01.00', '01.30', '02.00','02.30',
														'03.00', '03.30', '04.00', '04.30', '05.00','05.30',
														'06.00', '06.30', '07.00', '07.30', '08.00','08.30',
														'09.00', '09.30', '10.00', '10.30', '11.00','11.30'
														]}
							st.bar_chart(pd.DataFrame(nasatlx_history).set_index('Duration'))

						else:
							st.warning('Factor has not been selected.')


			else:
				st.error('Incorrect User Name / Password...')

		else:
			st.warning('Not logged in yet !')

	elif choice1 == 'Signup':
		st.subheader('Signup section')
		image = Image.open('signup.png')
		st.image(image)

		username = st.sidebar.text_input('User Name')
		password = st.sidebar.text_input('Password', type='password')
		confirm_password = st.sidebar.text_input('Confirm Password', type='password')
		uid = st.sidebar.text_input('Unique ID', type='password')

		if st.sidebar.checkbox('Signup'):
			if (username != '') and (password != '') and (confirm_password != '') and (uid != ''):
				if password != confirm_password:
					st.error('Both passwords are not matched')
				else:
					with open('credentials.txt', 'r') as f:
						cred = f.read().split("\n")
					length = len(cred)
					count = 0
					for elements in cred:
						element = elements.split(",")
						if (element[0] == username) and (element[1] == password):
							st.error('User Name / Password already exists. Try with new credentials.')
							break
						else:
							count += 1

					if count == length:
						with open('credentials.txt', 'a') as f:
							cred = '\n' + username + ',' + password + ',' + uid
							f.write(cred)
						st.success("Successfully signupped !")

			else:
				st.warning('Empty elements in the signup form')


	elif choice1 == 'Change credentials':
		st.subheader('Change credentials')
		image = Image.open('credentials.png')
		st.image(image)

		old_username = st.sidebar.text_input('Old User Name')
		old_password = st.sidebar.text_input('Old Password', type='password')

		new_username = st.sidebar.text_input('New User Name')
		new_password = st.sidebar.text_input('New Password', type='password')
		new_confirm_password = st.sidebar.text_input('Confirm New Password', type='password')
		new_uid = st.sidebar.text_input('Unique ID', type='password')

		if st.sidebar.checkbox('Change Credentials'):
			if new_password != new_confirm_password:
					st.error('Both new passwords are not matched')
			else:
				with open('credentials.txt', 'r') as f:
					cred = f.read().split("\n")

				broke = False
				for elements in cred:
					element = elements.split(",")
					if (element[0] == old_username) and (element[1] == old_password):
						broke = True
						break

				if broke == True:
					cred.remove(element[0]+','+element[1]+','+element[2])
					if new_uid == '':
						new_uid = elements[-1]
					cred.append(new_username + ',' + new_password + ',' + new_uid)

					data = ''
					for i in cred:
						data += i
						data += '\n'
					with open('credentials.txt', 'w') as f:
						print (data[:-1])
						f.write(data[:-1])
					st.success('Successfully changed credentials !')

				else:
					st.error('No such User Name / Password detected.')


	elif choice1 == 'Home':
		st.subheader('Welcome back to PSAS Home Section')
		image = Image.open('compuser.jpg')
		st.image(image, caption='A person who is working infront of a computer')
		color = st.color_picker('Pick A Color', '#00f900')
		quote = f'<p style="font-family:Courier; color:{color}; font-size: 20px;">We care you... You do your work...!</p>'
		st.markdown(quote, unsafe_allow_html=True)

if __name__ == '__main__':
	# Initial Firestore Configuration .....!
	cred = credentials.Certificate('new_key2.json') # Capture certificate

	notify_date = ''
	notify_time = ''

	try:
		firebase_admin.initialize_app(cred) # Initialize connection
		print ("Run through TRY part.")
	except:
		print ("Run through EXCEPT part.")
	finally:
		db = firestore.client() # Created the object
		print ("Run through FINALLY part.")

	WebApp()
