"""Pull from site like:
https://lasvegassun.com/blogs/talking-points/2020/dec/03/vegas-odds-nfl-picks-against-spread-betting-week13/
"""

headers, bodies = list(), list()
words = RAW.replace(">", "> ").replace("<", " <").split()
mode = "NORMAL"
header, body = list(), list()
for i, wi in enumerate(words):
    if mode == "NORMAL":
        if wi == "<strong>":
            s = " ".join(words[i:i+10])
            if s.find("Twitter") != -1 or s.find("Entertainment:") != -1:
                continue
            if s.find(" vs. ") == -1 and s.find(" at ") == -1:
                continue
            mode = "HEADER"
            continue
    if mode == "HEADER":
        if wi == "</strong>":
            headers.append(" ".join(header))
            header = list()
            mode = "BODY"
            continue
        header.append(wi)
    if mode == "BODY":
        if wi == "<em>":
            continue
        if wi == "</em>":
            bodies.append(" ".join(body))
            body = list()
            mode = "NORMAL"
            continue
        body.append(wi)

if len(headers) != len(bodies):
    raise Exception("Unexpected different size header/body")

for header, body in zip(headers, bodies):
    s = header.split("</strong>")[0]
    mid = " at " if s.find(" vs. ") == -1 else " vs. "
    team_1 = " ".join(s.split(mid)[0].split()[:-1])
    team_2 = s.split(mid)[1]
    home_team_name = team_1 if mid == " vs. " else team_2
    away_team_name = team_2 if mid == " vs. " else team_1
    winner_team_name = team_1
    pick_clause = s.split(mid)[0].split()[-1]
