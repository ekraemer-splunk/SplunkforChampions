# SplunkforChampions

Forwarder Setup (Currently Only Supports Windows)
Tl;dr: Forwarder grabs live data from a local API served over HTTP on port 2999, using the powershell equivalent of GET https://127.0.0.1:2999/liveclientdata/allgamedata. Returns live data that the player would know during the course of the game. It is documented well on the Game Client API 

Currently, live data is collected on each individual machine by calling the Game Client API - a local API which is served over HTTPS by the game, and is available locally on port 2999 

At the moment, the app uses a powershell script/scripted input on the Splunk Forwarder to call the API every second. In order to allow this script to execute in windows, we need to run `Set-ExecutionPolicy RemoteSigned` which I understand is not inherently too risky. The script is as follows:

add-type @"
using System.Net;
using System.Security.Cryptography.X509Certificates;
public class TrustAllCertsPolicy : ICertificatePolicy {
    public bool CheckValidationResult(
        ServicePoint srvPoint, X509Certificate certificate,
        WebRequest request, int certificateProblem) {
            return true;
        }
 }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
(Invoke-WebRequest -URI https://127.0.0.1:2999/liveclientdata/allgamedata -UseBasicParsing).Content

The Riot Games (postgame) API reports all timestamps in UTC, so in order to line up the live game data to the data given by the Riot Games API, we currently normalize all data to UTC in a props.conf file on the forwarder. In the future, the dates will be normalized to the user’s time zone

[powershell://LeagueClientAPI]
TZ = UTC
KV_MODE=json
TRUNCATE = 500000
SHOULD_LINEMERGE=false

The inputs.conf file on the forwarder is as follows:

[powershell://LeagueClientAPI]
script=. C:\Users\yangl\RiotConfFiles\callLeagueClientApi.ps1
schedule = 1
index = leagueclient
host = Splunk1Conf22


Install Instructions
Install a forwarder on the PCs which are running League of Legends
Run `Set-ExecutionPolicy RemoteSigned` on powershell
Save the input script specified above in a file called callLeagueClientApi.ps1
Add the powershell stanza to the inputs.conf file on the forwarder 
Restart the forwarder


Splunk Setup
Tl;dr: Scripted input calls Riot’s MatchInfo API and splits the returned json blob up by champion. Returns pretty comprehensive summary data - minions killed, total damage, total healed, champ level, name, damage to objectives, etc.

Currently, post-game summary data is collected by adding a scripted input to the search head, which calls Riot’s Match-V5 API and deblobs the data. As one single call will get data for all champions in the game, we authenticate against the API using only one player’s credentials (their gameName Splunk1conf22 and tagLine Spk01). 

These credentials are hardcoded into the script. In the future, the values will be set dynamically based on which players are actively in the game. 

Calling the getMatchInfo endpoint requires a matchID and an API key. 

The API key can be obtained by logging into the Riot API portal with the credentials Splunk1conf22, buttercup-g0 Currently, we are manually refreshing the API key every day, as we are currently awaiting a developer license from Riot. 

