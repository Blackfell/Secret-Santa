#!/usr/bin/python3

"""
AUTHOR : Blackfell

EMAIL : github@blackfell.net

SYNOPSIS: 
    This script will match users based on unique identities, in line with a provided
    blacklist of banned matches. The configuration is pulled from a yaml file which
    can be left to a default 'santa.yaml' or  specified as an optional command line 
    argument.

DEPENDENCIES:
    smtplib
    pyyaml
"""

import os
import re
import smtplib
import sys
import yaml
import random
import getopt

class Person:
    def __init__(self, name, email, disallowed):
        self.ban_count=0
        self.name = name
        self.email = email
        self.disallowed = disallowed
        self.match = ''
        self.match2 = ''    #Who's giving to them?
        self.ban_count = len(disallowed)
    
    def has_bad_match(self):
        if self.ban_count() > 0:
            return False
        else:
            return True
"""
Initialise person method, works for now.
"""
def initialise_person(name, email, blacklist, verbose):
    disallowed = []               #Everyone is allowed until proven otherwise
    #Test for blacklisted matches
    for bad_match in blacklist:
        if name in bad_match:
            if verbose == True:
                print('Blacklist for this person found: {}'.format(bad_match))
                #Identify which half of the match is disallowed for this person
            if bad_match[0] == name:
                disallowed.append(bad_match[1])
            else:
                disallowed.append(bad_match[0])
            if verbose == True:
                print('Disallowed person added as {}.'.format(disallowed))
    #Initialise the object
    name = Person(name, email, disallowed)
    return name

def get_config(config_file, verbose):
    config_file = os.path.join(os.path.dirname(__file__), config_file)
    with open(config_file) as f:
        y = yaml.load(f.read())
    if verbose == True:
        print('Config data read in, with imported keys of: {}.'.format(y.keys()))
    return y

def get_match(person, santas_list, verbose):
    #create a shuffled santas_list
    newlist=[]
    r = list(range(len(santas_list)))
    random.shuffle(r)
    for i in r:
        newlist.append(santas_list[i])
    #Start matching
    if verbose == True:
        print('[I]Trying to find a match for {}, excluding {}.'.format(person.name, person.disallowed))
    #Loop through and test all others as a viable match
    for i in range(len(newlist)):
        potential_match=newlist[i]
        if potential_match.match2 != '':#person already has a person giving to them
            if verbose == True:
                print('    [!]{} already has a match, continuing'.format(potential_match.name))
            continue
        #Test self assignment with object reference, not a name to avoid duplicates
        if potential_match == person: 
            if verbose == True:
                print('    [!]Self assignment detected for {}, continuing'.format(potential_match.name))
            continue
        if potential_match.name in person.disallowed:
            if verbose == True:
                print('    [!]Found blacklist for {} - {}, continuing.'.format(person.name, potential_match.name))
            continue
        else:
            if verbose == True:
                print('[M]Match found between {} and {}!'.format(person.name, potential_match.name))
            person.match = potential_match.name
            potential_match.match2=person.name
            return True                             #If match return True
    return False                                    #If no match, return False

def send_email(person, email, price_limit):
    #Setup headers
    msg = """Content-Type: text/plain; charset="utf-8"\nFrom: {sender}\nTo: {to}\nSubject: {subject}\n"""
    #Add body
    msg = msg + email['body']
    #substitute variables
    price_limit = str(price_limit)
    msg = msg.format(
            sender=email['sender'], 
            to=person.email, 
            subject=email['subject'],
            giver=person.name,
            reciever=person.match,
            price_limit=price_limit)
    try:
        smtp = smtplib.SMTP_SSL(email['server'],email['port'])
        smtp.login(email['sender'], email['loopy'])
        smtp.sendmail(email['sender'], person.email, msg)
        print('send ok')
    except Exception as e:
        print(e) 

def main(argv):
    #Set default variable values
    verbose = False
    disallowed = ''
    config_file = 'santa.yaml'
    santas_list = []
    send = False
    usage = '   $santa.py -i <config_file.yaml> --send --verbose'
    #CLI Inputs
    try:
        opts, args = getopt.getopt(argv,"hivs",["ifile=","send", "verbose"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-s", "--send"):
            send = True
        elif opt in ("-i", "--ifile"):
            config_file = arg
    if verbose == True:
        print('Running against {}, with verbosity of {} and send as {}.'.format(config_file, str(send), str(verbose)))
    #Herein lies the bulk of the main method
    try:
        #Import config data
        participant_data = get_config(config_file, verbose)
        participant_list = participant_data['participant_data']
        blacklist = participant_data['blacklist']
        email_data = participant_data['email']
        price_limit = participant_data['price_limit']

        #populate people objects, creating 'Santa's List'
        for name, email in participant_list.items():
            name = initialise_person(name, email , blacklist, verbose)
            santas_list.append(name)
        if verbose == True:
            print('[I]Santas List is:')
            for p in santas_list:
                print('    -{}'.format(p.name))

        #Sort participants by blacklist associated first
        santas_list.sort(key=lambda x: x.ban_count, reverse=True)   #sort by banned match count
        if verbose == True:
            print('[I]Santas list has been optimised to:')
            for p in santas_list:
                print('    -{}'.format(p.name))
        
        #loop through list and match
        for person in santas_list:
            matched = get_match(person, santas_list, verbose)
            if matched == False:
                raise ValueError('[X]Unable to find a match for {}, check your blacklist is not restrictive.'.format(person.name))
        
        #Matchin complete
        if verbose == True:
            print("""[!]Matches are:""")
            for person in santas_list:
                print('    [M]{} - {}'.format(person.name, person.match))
        if send == False:
            print("""[!]Pairing Complete!\nYou can send these pairings out by calling the script with the send options.\n\n   {}\n\nHave a nice day!""".format(usage))
        else:
            if verbose == True:
                print('[!]Sending emails.')
            for person in santas_list:
                print("Sending email to {}.".format(person.name))
                send_email(person, email_data, price_limit)
            

    except:
        fatal="""[!]Fatal Error matching your users, perhaps the blacklist is prohibitive,or the list too short. Try re-structuring these, adding more users, or removing disallowed matches altogether. If you still cannot get successful matchin, try running in verbose mode"""
        print('\033[91m' + fatal + '\033[0m')
        e = sys.exc_info()[0]
        print('\n\nException Detail:\n {}'.format(e))
        print(sys.exc_info())

if __name__ == '__main__':
    main(sys.argv[1:])
