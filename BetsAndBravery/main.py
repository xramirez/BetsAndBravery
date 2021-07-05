# So basically, praw is an API that allows you to access reddit (safely through their own systems/servers) and grab
# post titles, comments, and any extra information outside of that. The goal of this program is to take a Bets and
# Bravery thread, grab every single user comment in which a bet is made and the amount in which they bet, and lay it
# out nice and neat onto a .txt doc, OR, if we can manage, fit it entirely onto a google spreadsheet or excel
# spreadsheet.
import xlwt
from xlwt import Workbook
import praw  # lets us use reddit api
import re  # lets us use regular expressions

reddit = praw.Reddit(client_id='FFFWXVFNaeh9Vg', client_secret='R4NFvNJ6hFQmVn56Pirt5zUZhHpZfw',
                     user_agent='BetsAndBravery')

# this sets up the excel sheet that we are going to fit all the parsed data we need into
wb = Workbook()
sheet1 = wb.add_sheet('Sheet 1')
# I created an app in Reddit preferences (a personal app, since this won't have any commercial use), and it gave me
# the id, secret, and agent needed to create a reddit instance that I can browse through.
# so this is going to be set up at some point where somebody can input the new URL of whatever it is they want to
# parse through for now, we're just going to use an example post that has a few comments, just to test that what
# we're trying to grab, is actually grabbed
bbPost = reddit.submission(url='https://www.reddit.com/r/OnePiece/comments/ma3jfi/bets_and_bravery_chapter_1008/')


# in this function we're gonna take the username who left the comment and the body of each comment and parse it out
# Using string.split() so far is the best way I can see that happening. It allows us to isolate the pieces we're
# looking for and then we can start turning those individual small strings into usable information. How we're going
# to delete those other redundant strings is another thing entirely. We'll see how this goes.

# Reddit's API allows you to go through every single comment
# in a given post and print/parse the information you need out of it. My plan is to, for each comment body, turn it
# into a string, and take out the information I don't need. For example, someone might comment 450B - 75K, I want to
# turn it into three cells in 3 separate rows of a sheet that say "Bet 450", "B" "75,000"
# We can achieve this through the power of *** R E G U L A R  E X P R E S S I O N S ***
def parse_function(user_name, body_text):
    bet_number = None
    bet_option = None
    bet_amount = None
    print(user_name)
    # Split the body text into separate comments
    comment_lines = body_text.split()
    # creates an index in case we need to access the information of the next item in the list (spoiler alert: we do)
    index = 0
    for line in comment_lines:
        try:
            if line == '':
                continue
            # The first two regular expressions below are both specifically looking for Bet numbers and options
            # The regular expressions after that will be looking for bet amounts.
            # Basically, after we find a bet number, option, and amount, we can pass all 3 values to a new function that
            # will place the values into a spreadsheet (still deciding on google sheets or just an excel sheet)

            # The below regular expression looks specifically for bets, 3-4 numbers followed by a letter between A and J
            elif re.match(r"\d{3,4}[a-j]", line, flags=re.IGNORECASE):
                bet_number = (re.search(r"\d{3,4}", line, flags=re.IGNORECASE)).group()
                bet_option = (re.search(r"[a-j]", line, flags=re.IGNORECASE)).group()
                print(bet_number + " " + bet_option)
            # This is an alternate regular expression that looks for 3 digits followed by nothing, and checks to see if
            # the next string in the list of comments is just a letter, appends them together,
            # and makes that the new bet
            elif (re.match(r"\d{3,4}(?!\w)", line) and
                  re.match(r"(?<!\s)[a-j](?!\s)", comment_lines[index + 1], flags=re.IGNORECASE)):
                bet_number = re.search(r"\d{3,4}", line, flags=re.IGNORECASE).group()
                bet_option = re.search(r"(?<!\s)[a-j](?!\s)", comment_lines[index+1], flags=re.IGNORECASE).group()
                print(bet_number + " " + bet_option)
            # These regular expressions are going to look for bet amounts, starting with looking for K or M, or thousand
            # or million. We're also going to look for all in
            elif re.match(r"\d{1,3}(k|m)", line, flags=re.IGNORECASE):
                multiplier = re.search(r"k|m", line, flags=re.IGNORECASE).group()
                # Multiply the bet amount by 1,000 if k and 1,000,000 if m
                # The next step should be to check if anybody ever comments the full on number. It's not often tho
                if multiplier == 'k' or multiplier == 'K':
                    bet_amount = int(re.search(r"\d{1,3}", line, flags=re.IGNORECASE).group()) * 1000
                elif multiplier == 'm' or multiplier == 'M':
                    bet_amount = int(re.search(r"\d{1,3}", line, flags=re.IGNORECASE).group()) * 1000000
                print(bet_amount)
            # This one helped me realize we gotta make a try/catch, in case anybody has numbers at the end. Ugh.
            elif (re.match(r"\d{1,3}(?!\w)", line) and
                  re.match(r"(?<!\s)(k|m)(?!\s)", comment_lines[index + 1], flags=re.IGNORECASE)):
                multiplier = re.search(r"(?<!\s)(k|m)(?!\s)", comment_lines[index + 1], flags=re.IGNORECASE).group()
                line += comment_lines[index + 1][0]
                print("Bet amount: " + line)
        except IndexError:
            continue
        except TypeError:
            print("Trouble reading bet for " + user_name)
            continue
        index += 1
    print(comment_lines)


for top_level_comment in bbPost.comments:
    user = str(top_level_comment.author.name)
    body = str(top_level_comment.body)
    parse_function(user, body)
