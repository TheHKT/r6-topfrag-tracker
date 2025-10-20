from utils.webscraper import scrape_match_data
import os
import json

# Parses player data and returns a tuple of winners and loosers
def parse_player_data(match_data):
    raw_players = match_data.get("data").get("segments")
    winners = []
    loosers = []
    
    for i in range(0, 20):
        if(raw_players[i].get("type") != "overview"):
            continue
        player = {}
        player["username"] = raw_players[i].get("metadata").get("platformUserHandle")
        player["kills"] = raw_players[i].get("stats").get("kills").get("value")
        player["deaths"] = raw_players[i].get("stats").get("deaths").get("value")
        player["assists"] = raw_players[i].get("stats").get("assists").get("value")
        player["result"] = raw_players[i].get("metadata").get("result")
        player["headshots"] = raw_players[i].get("stats").get("headshots").get("value")
        player["teamkills"] = raw_players[i].get("stats").get("teamKills").get("value")
        player["aces"] = raw_players[i].get("stats").get("aces").get("value")
        player["suicides"] = raw_players[i].get("stats").get("suicides").get("value")
        player["firstBloods"] = raw_players[i].get("stats").get("firstBloods").get("value")
        player["firstDeaths"] = raw_players[i].get("stats").get("firstDeaths").get("value")
        player["clutches"] = raw_players[i].get("stats").get("clutches").get("value")
        player["clutchesLost"] = raw_players[i].get("stats").get("clutchesLost").get("value")
        player["clutches1v1"] = raw_players[i].get("stats").get("clutches1v1").get("value")
        player["clutches1v2"] = raw_players[i].get("stats").get("clutches1v2").get("value")
        player["clutches1v3"] = raw_players[i].get("stats").get("clutches1v3").get("value")
        player["clutches1v4"] = raw_players[i].get("stats").get("clutches1v4").get("value")
        player["clutches1v5"] = raw_players[i].get("stats").get("clutches1v5").get("value")
        player["clutchesLost1v1"] = raw_players[i].get("stats").get("clutchesLost1v1").get("value")
        player["clutchesLost1v2"] = raw_players[i].get("stats").get("clutchesLost1v2").get("value")
        player["clutchesLost1v3"] = raw_players[i].get("stats").get("clutchesLost1v3").get("value")
        player["clutchesLost1v4"] = raw_players[i].get("stats").get("clutchesLost1v4").get("value")
        player["clutchesLost1v5"] = raw_players[i].get("stats").get("clutchesLost1v5").get("value")
        player["kills1K"] = raw_players[i].get("stats").get("kills1K").get("value")
        player["kills2K"] = raw_players[i].get("stats").get("kills2K").get("value")
        player["kills3K"] = raw_players[i].get("stats").get("kills3K").get("value")
        player["kills4K"] = raw_players[i].get("stats").get("kills4K").get("value")
        player["kills5K"] = raw_players[i].get("stats").get("kills5K").get("value")
        player["kills6K"] = raw_players[i].get("stats").get("kills6K").get("value")
        if player.get("result") == "win":
            winners.append(player)
        else:
            loosers.append(player)

    return winners, loosers
def parse_match_data(match_data):
    raw_match = match_data.get("data").get("metadata")
    match = {}
    match["map"] = raw_match.get("sessionMapName")
    match["type"] = raw_match.get("sessionTypeName")
    match["mode"] = raw_match.get("sessionGameModeName")
    match["duration"] = raw_match.get("duration")
    match["cancelled"] = raw_match.get("isCancelledByAC")
    return match


def get_top_fragger(players):
    top_fragger = []
    max_kills = -1

    for player in players:
        if player["kills"] > max_kills:
            max_kills = player["kills"]
            top_fragger = [player]
        elif player["kills"] == max_kills:
            top_fragger.append(player)

    return top_fragger
def username_in_list(username, players):
    for player in players:
        if player["username"].lower() == username.lower():
            return True
    return False


async def check_for_matches(username):
    file_path = f'./store/{username}.json'
    old_match_data = None
    if os.path.exists(file_path):
        with open(f'./store/{username}.json', 'r') as f:
            old_match_data = json.load(f)
            
    match_data = await scrape_match_data(username, headless=False, save_to_file=True)
    if old_match_data and match_data.get("data").get("attributes").get("id") == old_match_data.get("data").get("attributes").get("id"):
        print("No new match found.")
        return None
    
    return match_data
def construct_message(match_data, username):
    winners, loosers = parse_player_data(match_data)
    match_info = parse_match_data(match_data)
    
    isWinner = username_in_list(username, winners)
    team = winners if isWinner else loosers
    enemy_team = loosers if isWinner else winners
    
    # Spieler-Daten für den User finden
    user_data = next((p for p in team if p["username"].lower() == username.lower()), None)
    
    topFragger = get_top_fragger(team)
    isUserTopFragger = username_in_list(username, topFragger)
    if(not isUserTopFragger):
        return None

    # Teammates auflisten (ohne User selbst)
    teammates = [p for p in team if p["username"].lower() != username.lower()]
    teammate_names = ", ".join([p["username"] for p in teammates[:5]])  # Erste 5 Teammates
    
    # Gegner auflisten
    enemy_names = ", ".join([p["username"] for p in enemy_team[:5]])

    # Besondere Achievements checken
    aces = user_data.get("aces", 0) if user_data else 0
    clutches = user_data.get("clutches", 0) if user_data else 0
    first_bloods = user_data.get("firstBloods", 0) if user_data else 0
    clutches_1v5 = user_data.get("clutches1v5", 0) if user_data else 0
    clutches_1v4 = user_data.get("clutches1v4", 0) if user_data else 0
    clutches_1v3 = user_data.get("clutches1v3", 0) if user_data else 0

    # Nachricht aufbauen
    if isWinner:
        msg = f"🏆 **SIEG!** 🏆\n"
        msg += f"**{username}** hat **GEWONNEN**! GG EZ! 🎉\n\n"
    else:
        msg = f"💀 **Knapp daneben...** 💀\n"
        msg += f"**{username}** hat **verloren**... Nächstes Mal! 😤\n\n"

    # Top Fragger Section
    if isUserTopFragger:
        msg += f"🎯 **{username} WAR DER ABSOLUTE KILLER!** 🎯\n"
        msg += f"Mit **{user_data['kills']} Kills** hat er das Match dominiert! 💀\n"
    else:
        top_player = topFragger[0]
        msg += f"📊 **Top Fragger:** **{top_player['username']}** mit **{top_player['kills']} Kills** 👑\n"

    # User Stats
    if user_data:
        kd_ratio = user_data['kills'] / user_data['deaths'] if user_data['deaths'] > 0 else user_data['kills']
        msg += f"\n**{username}'s Stats:**\n"
        msg += f"```{user_data['kills']}/{user_data['deaths']}/{user_data['assists']} | K/D: {kd_ratio:.2f}```\n"
        msg += f"**Headshots:** {user_data['headshots']} 🎯 | **First Bloods:** {first_bloods} 🔪\n"

    # Special Achievements
    achievements = []
    if aces > 0:
        achievements.append(f"**{aces} ACE{'S' if aces > 1 else ''}** 🃏")
    if clutches_1v5 > 0:
        achievements.append(f"**{clutches_1v5} 1v5 CLUTCH{'ES' if clutches_1v5 > 1 else ''}** 🤯")
    elif clutches_1v4 > 0:
        achievements.append(f"**{clutches_1v4} 1v4 CLUTCH{'ES' if clutches_1v4 > 1 else ''}** 🫡")
    elif clutches_1v3 > 0:
        achievements.append(f"**{clutches_1v3} 1v3 CLUTCH{'ES' if clutches_1v3 > 1 else ''}** 🔥")
    elif clutches > 0:
        achievements.append(f"**{clutches} CLUTCH{'ES' if clutches > 1 else ''}** 💪")
    
    if achievements:
        msg += f"\n**🔥 BESONDERE ERFOLGE:** {' | '.join(achievements)}\n"

    # Teams Overview
    msg += f"\n**🤝 TEAMKAMERADEN:** {teammate_names}\n"
    msg += f"**👥 GEGNER:** {enemy_names}\n"

    # Match Info
    msg += f"\n**🎮 MATCH INFO:** {match_info['map']} | {match_info['mode']} | {match_info['type']}\n"
    
    # Motivational Footer
    if isWinner and isUserTopFragger:
        msg += "\n**UNSTOPPBAR! Die Lobby wurde dem Erdboden gleichgemacht!** 💥"
    elif isWinner:
        msg += "\n**Teamwork macht den Dreamwork!** 🤝"
    else:
        msg += "\n**Bleib dran, das nächste Match ist deins!** ⚡"

    return msg