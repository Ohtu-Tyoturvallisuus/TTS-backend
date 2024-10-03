## Käyttääksesi speech to textiä, kun pyörität backendiä lokaalisti:

Lisää .env-tiedostoon seuraavat rivit:

SPEECH_KEY=<your_speech_key>
SPEECH_SERVICE_REGION=<your_speech_service_region>

Speech key ja service region löytyvät seuraavasti:

Avaa Azure portalissa telinekatajan hakemisto. Klikkaa All resources 
-> tts-dev-speech
-> Resource management
-> Keys and Endpoint

SPEECH_KEY:n arvo voi olla joko key 1 tai key 2.
SPEECH_SERVICE_REGION:n arvo on kohdassa Location/Region
