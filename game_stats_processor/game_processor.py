from typing import Dict
from team_stats import TeamStats
import cloudscraper
import json
import time

# teamcode = A|B where A is home and B visitor


def add_match_stats(team_stats: TeamStats, match, teamcode):
    team_stats.group_name = match['group_name']

    if teamcode == 'A':
        team_stats.goals_allowed = team_stats.goals_allowed + \
            int('0'+match['fs_B'])
        team_stats.goals = team_stats.goals + int('0'+match['fs_A'])
        if match['winner'] == 'Home':
            team_stats.wins = team_stats.wins + 1
            team_stats.points = team_stats.points + 3
        if match['winner'] == 'Away':
            team_stats.losses = team_stats.losses + 1
            if match['club_B_id'] not in team_stats.lost_teams:
                team_stats.lost_teams.append(match['club_B_id'])
    else:
        team_stats.goals_allowed = team_stats.goals_allowed + \
            int('0'+match['fs_A'])
        team_stats.goals = team_stats.goals + int('0'+match['fs_B'])

        if match['winner'] == 'Home':
            team_stats.losses = team_stats.losses + 1
            if match['club_A_id'] not in team_stats.lost_teams:
                team_stats.lost_teams.append(match['club_A_id'])
        if match['winner'] == 'Away':
            team_stats.wins = team_stats.wins + 1
            team_stats.points = team_stats.points + 3

    if match['winner'] == 'Tie':
        team_stats.ties = team_stats.ties + 1
        team_stats.points = team_stats.points + 1

    return team_stats


def get_group(team_stat: TeamStats):
    return team_stat.group_name


def calculate_ranking(stats: Dict):

    ordered_list = []
    # copy the dict items to list structure
    for stat in stats.values():
        ordered_list.append(stat)

    # sort list by groups
    ordered_list.sort(key=get_group)

    # Bubble sort team rankings
    n = len(ordered_list)
    for i in range(n):

        for j in range(0, n-i-1):
            goal_difference = ordered_list[j].goals - ordered_list[j].goals_allowed
            goal_difference_next = ordered_list[j+1].goals - ordered_list[j+1].goals_allowed

            if (ordered_list[j].points < ordered_list[j+1].points ) and ordered_list[j].group_name == ordered_list[j+1].group_name:
                ordered_list[j], ordered_list[j + 1] = ordered_list[j+1], ordered_list[j]
            elif (ordered_list[j].points == ordered_list[j+1].points and goal_difference < goal_difference_next and ordered_list[j].group_name == ordered_list[j+1].group_name):
                ordered_list[j], ordered_list[j + 1] = ordered_list[j+1], ordered_list[j]


    return ordered_list


def print_table(ordered_list):

    print_header = True
    previous_group = ""
    for i in range(len(ordered_list)):

        if previous_group != ordered_list[i].group_name:
            previous_group = ordered_list[i].group_name
            print("")
            print(ordered_list[i].group_name)
            print("                                   " + " O  " +
                  "V  " + "T  " + "H " + "   M" + "    P")

        games = ordered_list[i].wins + \
            ordered_list[i].losses + ordered_list[i].ties
        print(ordered_list[i].team_name +
              str(games).rjust(2) + " " +
              str(ordered_list[i].wins).rjust(2) + " " +
              str(ordered_list[i].ties).rjust(2) + " " +
              str(ordered_list[i].losses).rjust(2) + " " +
              str(ordered_list[i].goals).rjust(2) + "-" +
              str(ordered_list[i].goals_allowed).ljust(2) + " " +
              str(ordered_list[i].points).rjust(3))


def scrape_matches():

    i = 0
    response = None
    while True and i < 50:

        try:
            # print("Scraping... " + str(i))
            scraper = cloudscraper.create_scraper()
            response = scraper.get("https://spl.torneopal.net/taso/rest/getMatches?competition_id=etejp21&category_id=P11&tpid=-594016905", headers={
                "origin":"https://tulospalvelu.palloliitto.fi",
                "referer":"https://tulospalvelu.palloliitto.fi/",
                "accept":"json/df8e84j9xtdz269euy3h",
                "host": "spl.torneopal.net",
                "path": "/taso/rest/getMatches?competition_id=etejp21&category_id=P11&tpid=-594016905",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "sec-gpc": "1"
            }).json()
            break
        except Exception as e:
            time.sleep(0.1)
            pass

        i = i + 1
    
    if response == None:
        raise Exception("Getting matches didn't succeed!")
          
    return response


response = scrape_matches()

stats = {}
for match in response['matches']:

    team_a_id = match['team_A_id'] + match['group_name']
    team_b_id = match['team_B_id'] + match['group_name']

    # Let's check if team A already is in stats collection
    if team_a_id in stats:
        team_stats_a = stats[team_a_id]
    else:
        team_stats_a = TeamStats()
        team_stats_a.team_name = match['team_A_name'].ljust(35)
        team_stats_a.group_name = match['group_name']

    # Let's check if team B already is in stats collection
    if team_b_id in stats:
        team_stats_b = stats[team_b_id]
    else:
        team_stats_b = TeamStats()
        team_stats_b.team_name = match['team_B_name'].ljust(35)
        team_stats_a.group_name = match['group_name']

    team_stats_a = add_match_stats(team_stats_a, match, 'A')
    team_stats_b = add_match_stats(team_stats_b, match, 'B')

    stats[team_a_id] = team_stats_a
    stats[team_b_id] = team_stats_b


stats = calculate_ranking(stats)
print_table(stats)
