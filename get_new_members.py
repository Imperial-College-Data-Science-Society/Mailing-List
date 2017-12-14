import pandas as pd

PRINT_LOS = False # Pint level of study

# List of all columns in union list
union_columns = ['Date', 'Order No', 'CID', 'Login', 'First Name', 'Surname',
       'Email', 'Gender', 'Campus', 'Department', 'Program Description',
       'Study Date Start', 'Study Date End', 'Study Year']

# List of useful columns in union list
useful_union_columns = ['First Name', 'Surname',
       'Email', 'Gender', 'Department'] 
# 'Program Description' is used in program to get the level of study but doesn't appear in output file


# Dictionary to match union list column names to MailChimp list column names
union_to_mc_dic = {
	'Email' : 'Email Address',
 	'First Name' : 'First Name', 
	'Surname' : 'Last Name', 
	'Department' : 'Degree',
        'Gender' : 'Gender',
}


# Get the size (in lines) of the footer to be removed at the end of union list file
footer_size = 0
with open('Members_Report.csv', 'r') as union_file:
	lines = union_file.readlines()
	for i in range(len(lines)):
		if lines[i].startswith("Life "):
			footer_size = len(lines) - i

# Open union list file
union_filename = "Members_Report.csv"
print "Read Union Data from file"
# WARNING : I skip 1 line at the top and several at the bottom because I only want the Full Member section in the file 'Members_Report' 
try:
	union_data = pd.read_csv(union_filename, engine='python', skiprows=1, skipfooter=footer_size)
except IOError:
	print "Error : Please download the union member list as csv from the union website and place it in this folder as 'Members_Report.csv'"
	exit(0)


print "Process the Program Description information to get the Level of Study"
def process_program_description(row):
        if type(row['Program Description']) != str:
                return "Other"
        if any(x in row['Program Description'] for x in ['PhD']):
                val = 'PhD'
        elif any(x in row['Program Description'] for x in ['MEng', 'MSc', 'MRes']):
                val = 'Masters'
        elif any(x in row['Program Description'] for x in ['BEng', 'BSc']):
                val = 'Bachelor'
        elif any(x in row['Program Description'] for x in ['Research']):
                val = 'PhD or Higher'
        else:
                val = row['Program Description']
        return val

# Add the Level of Study column
union_data['Level of Study'] = union_data.apply(process_program_description, axis=1)
if (PRINT_LOS == True):
	print union_data["Level of Study"].value_counts()


print "Drop useless union data columns"
drop_list = [x for x in union_columns if x not in useful_union_columns]
union_data.drop(drop_list, inplace=True, axis=1)
print "Modify column names to match MailChimp"
union_data.rename(columns = union_to_mc_dic, inplace=True)


print "Read Mailchimp data (Subscribed members, non subscribed members and cleaned members)"
try:
	mc_data = pd.read_csv('subscribed_members.csv')
except IOError:
	print "\nError : File 'subscibed_members.csv' not found"
	print "Please download the MailChimp list of subscribed members from the MailChimp website and place it in this folder as 'subscribed_members.csv'"
	exit(0)
try:
	mc_data_uns = pd.read_csv('unsubscribed_members.csv')
except IOError:
	print "\nError : File 'unsubscribed_members.csv' not found"
	print "Please download the MailChimp list of unsubscribed members from the MailChimp website and place it in this folder as 'unsubscribed_members.csv'"
	exit(0)
try:
	mc_data_clean = pd.read_csv('cleaned_members.csv')
except IOError:
	print "\nError : File 'cleaned_members.csv' not found"
	print "Please download the MailChimp list of cleaned members from the MailChimp website and place it in this folder as 'cleaned_members.csv'"
	exit(0)

# Lower case all email addresses in mc_lists (all union adresses are lower case)
#mc_data['Email Address'] = mc_data['Email Address'].str.lower()
#mc_data_uns['Email Address'] = mc_data_uns['Email Address'].str.lower()
#mc_data_clean['Email Address'] = mc_data_clean['Email Address'].str.lower()

print "Get the members in union list that are not in MailChimp list"
new_members = union_data
new_members = new_members[~new_members['Email Address'].str.lower().isin(mc_data['Email Address'].str.lower())]
new_members = new_members[~new_members['Email Address'].str.lower().isin(mc_data_uns['Email Address'].str.lower())]
new_members = new_members[~new_members['Email Address'].str.lower().isin(mc_data_clean['Email Address'].str.lower())]
print "Number of new members to add to Mailchimp : %d" %len(new_members)

# Write the list of members to be added to MailChimp
new_members.to_csv('new_members.csv', index=False)

print "Look out for new members who previously unsubscibed"
previously_unsubscribed = union_data
previously_unsubscribed = previously_unsubscribed[previously_unsubscribed['Email Address'].str.lower().isin(mc_data_uns['Email Address'].str.lower())]
print "Number of new members who previously unsubscribed : %d" %len(previously_unsubscribed)

# Write the list of members to be added to MailChimp
previously_unsubscribed.to_csv('previously_unsub_members.csv', index=False)


